module.exports = async function(context) {
  const fileSize = context.fileSize || 0;
  const changes = context.changes || [];
  
  // Если файл большой или изменений много
  if (fileSize > 100000 || changes.length > 10) {
    // Разбить задачу на подзадачи
    return {
      strategy: 'incremental',
      maxChangesPerOperation: 5,
      waitBetweenOperations: 1000
    };
  }
  
  return {
    strategy: 'default'
  };
};
