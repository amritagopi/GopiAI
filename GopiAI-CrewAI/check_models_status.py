    # Заменено на использование path_manager: sys.path.append('.')

from llm_rotation_config import rate_limit_monitor, LLM_MODELS_CONFIG

def _get_usage_safe(monitor, model_id):
    # Prefer method-based access to satisfy static type checkers
    if hasattr(monitor, "get_usage"):
        try:
            data = monitor.get_usage(model_id)  # type: ignore[attr-defined]
            return data or {"rpm": 0, "tpm": 0, "rpd": 0}
        except Exception:
            pass
    if hasattr(monitor, "get_model_usage"):
        try:
            data = monitor.get_model_usage(model_id)  # type: ignore[attr-defined]
            return data or {"rpm": 0, "tpm": 0, "rpd": 0}
        except Exception:
            pass
    # Fallback for legacy attribute if present
    if hasattr(monitor, "usage"):
        try:
            # mypy/pyright: attribute exists guarded by hasattr
            return getattr(monitor, "usage").get(model_id, {"rpm": 0, "tpm": 0, "rpd": 0})  # type: ignore[attr-defined]
        except Exception:
            pass
    return {"rpm": 0, "tpm": 0, "rpd": 0}

print("=== СТАТУС ВСЕХ МОДЕЛЕЙ ===\n")

print("🔍 Blacklist статус:")
blacklist = rate_limit_monitor.get_blacklist_status()
if blacklist:
    for model_id, remaining_time in blacklist.items():
        print(f"  🚫 {model_id}: заблокирована еще {remaining_time} секунд")
else:
    print("  ✅ Нет заблокированных моделей")

print("\n📊 Детальная статистика по моделям:")
for model in LLM_MODELS_CONFIG:
    model_id = model['id']
    usage = _get_usage_safe(rate_limit_monitor, model_id)
    
    # Access via getattr to satisfy static type checkers when attributes are dynamic
    is_blocked = getattr(rate_limit_monitor, "is_model_blocked", lambda _mid: False)(model_id)  # type: ignore[attr-defined]
    can_use = getattr(rate_limit_monitor, "can_use", lambda _mid: False)(model_id)  # type: ignore[attr-defined]
    
    print(f"\n🎯 {model['name']} ({model_id}):")
    print(f"   Приоритет: {model['priority']}")
    print(f"   Лимиты: RPM={model['rpm']}, TPM={model['tpm']}, RPD={model['rpd']}")
    print(f"   Использовано: RPM={usage.get('rpm', 0)}, TPM={usage.get('tpm', 0)}, RPD={usage.get('rpd', 0)}")
    print(f"   Статус: {'🚫 ЗАБЛОКИРОВАНА' if is_blocked else '✅ Доступна' if can_use else '⚠️ Лимиты исчерпаны'}")

print("\n📈 Общая статистика:")
available_count = sum(
    1
    for m in LLM_MODELS_CONFIG
    if not getattr(rate_limit_monitor, "is_model_blocked", lambda _mid: False)(m["id"])  # type: ignore[attr-defined]
    and getattr(rate_limit_monitor, "can_use", lambda _mid: False)(m["id"])  # type: ignore[attr-defined]
)
blocked_count = len(blacklist) if blacklist else 0
limit_exceeded_count = sum(
    1
    for m in LLM_MODELS_CONFIG
    if not getattr(rate_limit_monitor, "is_model_blocked", lambda _mid: False)(m["id"])  # type: ignore[attr-defined]
    and not getattr(rate_limit_monitor, "can_use", lambda _mid: False)(m["id"])  # type: ignore[attr-defined]
)

print(f"   ✅ Доступно моделей: {available_count}")
print(f"   🚫 Заблокировано: {blocked_count}")
print(f"   ⚠️ Лимиты исчерпаны: {limit_exceeded_count}")
print(f"   📊 Всего моделей: {len(LLM_MODELS_CONFIG)}")