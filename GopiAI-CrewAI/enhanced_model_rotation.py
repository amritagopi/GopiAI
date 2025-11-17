#!/usr/bin/env python3
"""
Enhanced Model Rotation System for GopiAI
Addresses critical issues with rate limiting and model switching
"""

import time
import threading
import logging
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from llm_rotation_config import LLM_MODELS_CONFIG, rate_limit_monitor

logger = logging.getLogger(__name__)

class ModelHealth(Enum):
    HEALTHY = "healthy"
    RATE_LIMITED = "rate_limited"
    OVERLOADED = "overloaded"
    ERROR = "error"
    BLACKLISTED = "blacklisted"

@dataclass
class ModelStatus:
    health: ModelHealth = ModelHealth.HEALTHY
    last_error: Optional[str] = None
    error_count: int = 0
    last_success: float = field(default_factory=time.time)
    last_attempt: float = field(default_factory=time.time)
    consecutive_failures: int = 0
    avg_response_time: float = 0.0
    total_requests: int = 0

class EnhancedModelRotator:
    """Enhanced model rotation with intelligent fallback and health monitoring"""
    
    def __init__(self):
        self.model_status: Dict[str, ModelStatus] = {}
        self.lock = threading.RLock()
        self.circuit_breaker_threshold = 3
        self.circuit_breaker_timeout = 300  # 5 minutes
        self.health_check_interval = 60  # 1 minute
        self.last_health_check = time.time()
        
        # Initialize status for all models
        for model in LLM_MODELS_CONFIG:
            self.model_status[model["id"]] = ModelStatus()
    
    def get_best_model(self, task_type: str, exclude_models: List[str] = None) -> Optional[str]:
        """
        Get the best available model for a task with intelligent selection
        
        Args:
            task_type: Type of task (dialog, code, etc.)
            exclude_models: Models to exclude from selection
            
        Returns:
            Model ID or None if no models available
        """
        exclude_models = exclude_models or []
        
        with self.lock:
            # Perform health check if needed
            self._perform_health_check()
            
            # Filter suitable models
            suitable_models = []
            for model in LLM_MODELS_CONFIG:
                if (
                    task_type in model["type"] and
                    not model.get("deprecated", False) and
                    model["id"] not in exclude_models and
                    not rate_limit_monitor.is_model_blocked_safe(model["id"])
                ):
                    suitable_models.append(model)
            
            if not suitable_models:
                logger.warning(f"No suitable models found for task_type: {task_type}")
                return None
            
            # Score and rank models
            scored_models = []
            for model in suitable_models:
                score = self._calculate_model_score(model)
                scored_models.append((model, score))
            
            # Sort by score (higher is better)
            scored_models.sort(key=lambda x: x[1], reverse=True)
            
            # Try models in order of score
            for model, score in scored_models:
                model_id = model["id"]
                
                # Check if model can handle request
                if rate_limit_monitor.can_use(model_id):
                    logger.info(f"Selected model {model_id} (score: {score:.3f})")
                    return model_id
            
            logger.warning("All suitable models are at capacity")
            return None
    
    def _calculate_model_score(self, model: Dict) -> float:
        """Calculate a composite score for model selection"""
        model_id = model["id"]
        status = self.model_status.get(model_id, ModelStatus())
        
        # Base score from configuration
        base_score = model.get("base_score", 0.5)
        
        # Health penalty
        health_penalty = 0.0
        if status.health == ModelHealth.RATE_LIMITED:
            health_penalty = 0.3
        elif status.health == ModelHealth.OVERLOADED:
            health_penalty = 0.4
        elif status.health == ModelHealth.ERROR:
            health_penalty = 0.5
        elif status.health == ModelHealth.BLACKLISTED:
            health_penalty = 0.9
        
        # Consecutive failures penalty
        failure_penalty = min(status.consecutive_failures * 0.1, 0.4)
        
        # Recent success bonus
        time_since_success = time.time() - status.last_success
        success_bonus = max(0, 0.2 - (time_since_success / 3600))  # Decay over 1 hour
        
        # Load-based scoring
        usage = rate_limit_monitor.usage.get(model_id, {"rpm": 0, "tpm": 0, "rpd": 0})
        model_config = rate_limit_monitor.models.get(model_id, model)
        
        # Calculate load percentage
        rpm_load = usage["rpm"] / max(model_config.get("rpm", 1), 1)
        tpm_load = usage["tpm"] / max(model_config.get("tpm", 1), 1)
        rpd_load = usage["rpd"] / max(model_config.get("rpd", 1000), 1)
        
        max_load = max(rpm_load, tpm_load, rpd_load)
        load_penalty = max_load * 0.3
        
        # Priority bonus (lower priority number = higher bonus)
        priority_bonus = (10 - model.get("priority", 5)) * 0.02
        
        final_score = (
            base_score
            - health_penalty
            - failure_penalty
            - load_penalty
            + success_bonus
            + priority_bonus
        )
        
        return max(0.0, min(1.0, final_score))
    
    def record_success(self, model_id: str, response_time: float = 0.0):
        """Record successful model usage"""
        with self.lock:
            if model_id not in self.model_status:
                self.model_status[model_id] = ModelStatus()
            
            status = self.model_status[model_id]
            status.health = ModelHealth.HEALTHY
            status.last_success = time.time()
            status.last_attempt = time.time()
            status.consecutive_failures = 0
            status.total_requests += 1
            
            # Update average response time
            if response_time > 0:
                if status.avg_response_time == 0:
                    status.avg_response_time = response_time
                else:
                    # Exponential moving average
                    status.avg_response_time = (
                        status.avg_response_time * 0.8 + response_time * 0.2
                    )
            
            logger.debug(f"Recorded success for {model_id} (response_time: {response_time:.2f}s)")
    
    def record_failure(self, model_id: str, error: str):
        """Record model failure and update health status"""
        with self.lock:
            if model_id not in self.model_status:
                self.model_status[model_id] = ModelStatus()
            
            status = self.model_status[model_id]
            status.last_error = error
            status.error_count += 1
            status.consecutive_failures += 1
            status.last_attempt = time.time()
            
            # Determine health based on error type
            error_lower = error.lower()
            if any(keyword in error_lower for keyword in [
                'quota', 'rate limit', 'resource_exhausted', '429'
            ]):
                status.health = ModelHealth.RATE_LIMITED
                # Auto-blacklist for rate limiting
                rate_limit_monitor.mark_model_unavailable(model_id, duration=1800)  # 30 min
            elif any(keyword in error_lower for keyword in [
                'overloaded', '503', 'unavailable', 'service_unavailable'
            ]):
                status.health = ModelHealth.OVERLOADED
                rate_limit_monitor.mark_model_unavailable(model_id, duration=600)  # 10 min
            else:
                status.health = ModelHealth.ERROR
            
            # Circuit breaker logic
            if status.consecutive_failures >= self.circuit_breaker_threshold:
                status.health = ModelHealth.BLACKLISTED
                rate_limit_monitor.mark_model_unavailable(
                    model_id, 
                    duration=self.circuit_breaker_timeout
                )
                logger.warning(
                    f"Circuit breaker triggered for {model_id} "
                    f"after {status.consecutive_failures} failures"
                )
            
            logger.warning(f"Recorded failure for {model_id}: {error}")
    
    def _perform_health_check(self):
        """Periodic health check and status reset"""
        now = time.time()
        if now - self.last_health_check < self.health_check_interval:
            return
        
        self.last_health_check = now
        
        for model_id, status in self.model_status.items():
            # Auto-heal models that have been healthy for a while
            time_since_failure = now - status.last_attempt
            
            if (
                status.health in [ModelHealth.ERROR, ModelHealth.OVERLOADED] and
                time_since_failure > 300  # 5 minutes
            ):
                # Gradual recovery
                if status.consecutive_failures > 0:
                    status.consecutive_failures = max(0, status.consecutive_failures - 1)
                
                if status.consecutive_failures == 0:
                    status.health = ModelHealth.HEALTHY
                    logger.info(f"Model {model_id} recovered to healthy status")
    
    def get_model_statistics(self) -> Dict[str, Dict]:
        """Get detailed statistics for all models"""
        with self.lock:
            stats = {}
            for model_id, status in self.model_status.items():
                usage = rate_limit_monitor.usage.get(model_id, {})
                stats[model_id] = {
                    "health": status.health.value,
                    "error_count": status.error_count,
                    "consecutive_failures": status.consecutive_failures,
                    "avg_response_time": status.avg_response_time,
                    "total_requests": status.total_requests,
                    "last_success_ago": time.time() - status.last_success,
                    "is_blacklisted": rate_limit_monitor.is_model_blocked_safe(model_id),
                    "current_usage": usage,
                    "last_error": status.last_error
                }
            return stats
    
    def force_model_recovery(self, model_id: str):
        """Manually force a model back to healthy status"""
        with self.lock:
            if model_id in self.model_status:
                self.model_status[model_id].health = ModelHealth.HEALTHY
                self.model_status[model_id].consecutive_failures = 0
                logger.info(f"Forced recovery for model {model_id}")

# Global enhanced rotator instance
enhanced_rotator = EnhancedModelRotator()

def get_best_model_enhanced(task_type: str, exclude_models: List[str] = None) -> Optional[str]:
    """Enhanced model selection function"""
    return enhanced_rotator.get_best_model(task_type, exclude_models)

def record_model_success(model_id: str, response_time: float = 0.0):
    """Record successful model usage"""
    enhanced_rotator.record_success(model_id, response_time)

def record_model_failure(model_id: str, error: str):
    """Record model failure"""
    enhanced_rotator.record_failure(model_id, error)

def get_model_health_stats() -> Dict[str, Dict]:
    """Get model health statistics"""
    return enhanced_rotator.get_model_statistics()

if __name__ == "__main__":
    # Test the enhanced rotator
    print("Testing Enhanced Model Rotator")
    
    # Test model selection
    model = get_best_model_enhanced("dialog")
    print(f"Selected model for dialog: {model}")
    
    # Simulate some failures
    if model:
        record_model_failure(model, "Rate limit exceeded")
        record_model_failure(model, "Service overloaded")
    
    # Get stats
    stats = get_model_health_stats()
    for model_id, stat in stats.items():
        print(f"{model_id}: {stat['health']} ({stat['consecutive_failures']} failures)")