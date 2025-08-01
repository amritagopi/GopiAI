/**
 * Тесты для унифицированного инструмента файловой системы
 * 
 * Автор: GopiAI System
 * Версия: 1.0.0
 */

const { UnifiedFileSystemTool } = require('../src/tools/unified_filesystem_tools');
const fs = require('fs').promises;
const path = require('path');

class FileSystemToolTester {
    constructor() {
        this.tool = new UnifiedFileSystemTool();
        this.testDir = './test_temp';
        this.testResults = [];
    }

    /**
     * Запуск всех тестов
     */
    async runAllTests() {
        console.log('🚀 Запуск тестов унифицированного инструмента файловой системы...\n');

        try {
            await this.setupTestEnvironment();
            
            await this.testWriteFile();
            await this.testReadFile();
            await this.testListDirectory();
            await this.testCopyFile();
            await this.testMoveFile();
            await this.testSearchFiles();
            await this.testGetFileInfo();
            await this.testDirectoryTree();
            await this.testCreateDirectory();
            await this.testDeleteFile();
            await this.testFileSystemStatus();
            
            await this.cleanupTestEnvironment();
            
            this.printResults();
            
        } catch (error) {
            console.error('❌ Критическая ошибка при выполнении тестов:', error.message);
        }
    }

    /**
     * Настройка тестовой среды
     */
    async setupTestEnvironment() {
        try {
            await fs.mkdir(this.testDir, { recursive: true });
            console.log('✅ Тестовая среда настроена');
        } catch (error) {
            console.error('❌ Ошибка настройки тестовой среды:', error.message);
        }
    }

    /**
     * Очистка тестовой среды
     */
    async cleanupTestEnvironment() {
        try {
            await fs.rmdir(this.testDir, { recursive: true });
            console.log('✅ Тестовая среда очищена');
        } catch (error) {
            console.error('❌ Ошибка очистки тестовой среды:', error.message);
        }
    }

    /**
     * Тест записи файла
     */
    async testWriteFile() {
        const testName = 'Запись файла';
        try {
            const result = await this.tool.execute({
                action: 'write',
                data: {
                    path: path.join(this.testDir, 'test.txt'),
                    content: 'Тестовое содержимое файла\nВторая строка'
                }
            });

            if (result.success) {
                this.addTestResult(testName, true, 'Файл успешно записан');
            } else {
                this.addTestResult(testName, false, result.error);
            }
        } catch (error) {
            this.addTestResult(testName, false, error.message);
        }
    }

    /**
     * Тест чтения файла
     */
    async testReadFile() {
        const testName = 'Чтение файла';
        try {
            const result = await this.tool.execute({
                action: 'read',
                data: {
                    path: path.join(this.testDir, 'test.txt')
                }
            });

            if (result.success && result.files[0].content.includes('Тестовое содержимое')) {
                this.addTestResult(testName, true, 'Файл успешно прочитан');
            } else {
                this.addTestResult(testName, false, result.error || 'Неверное содержимое');
            }
        } catch (error) {
            this.addTestResult(testName, false, error.message);
        }
    }

    /**
     * Тест списка директории
     */
    async testListDirectory() {
        const testName = 'Список директории';
        try {
            const result = await this.tool.execute({
                action: 'list',
                data: {
                    path: this.testDir,
                    detailed: true
                }
            });

            if (result.success && result.items.length > 0) {
                this.addTestResult(testName, true, `Найдено ${result.items.length} элементов`);
            } else {
                this.addTestResult(testName, false, result.error || 'Пустая директория');
            }
        } catch (error) {
            this.addTestResult(testName, false, error.message);
        }
    }

    /**
     * Тест копирования файла
     */
    async testCopyFile() {
        const testName = 'Копирование файла';
        try {
            const result = await this.tool.execute({
                action: 'copy',
                data: {
                    source: path.join(this.testDir, 'test.txt'),
                    destination: path.join(this.testDir, 'test_copy.txt')
                }
            });

            if (result.success) {
                this.addTestResult(testName, true, 'Файл успешно скопирован');
            } else {
                this.addTestResult(testName, false, result.error);
            }
        } catch (error) {
            this.addTestResult(testName, false, error.message);
        }
    }

    /**
     * Тест перемещения файла
     */
    async testMoveFile() {
        const testName = 'Перемещение файла';
        try {
            const result = await this.tool.execute({
                action: 'move',
                data: {
                    source: path.join(this.testDir, 'test_copy.txt'),
                    destination: path.join(this.testDir, 'test_moved.txt')
                }
            });

            if (result.success) {
                this.addTestResult(testName, true, 'Файл успешно перемещён');
            } else {
                this.addTestResult(testName, false, result.error);
            }
        } catch (error) {
            this.addTestResult(testName, false, error.message);
        }
    }

    /**
     * Тест поиска файлов
     */
    async testSearchFiles() {
        const testName = 'Поиск файлов';
        try {
            const result = await this.tool.execute({
                action: 'search',
                data: {
                    path: this.testDir,
                    pattern: '*.txt',
                    maxResults: 10
                }
            });

            if (result.success && result.results.length > 0) {
                this.addTestResult(testName, true, `Найдено ${result.results.length} файлов`);
            } else {
                this.addTestResult(testName, false, result.error || 'Файлы не найдены');
            }
        } catch (error) {
            this.addTestResult(testName, false, error.message);
        }
    }

    /**
     * Тест получения информации о файле
     */
    async testGetFileInfo() {
        const testName = 'Информация о файле';
        try {
            const result = await this.tool.execute({
                action: 'info',
                data: {
                    path: path.join(this.testDir, 'test.txt')
                }
            });

            if (result.success && result.type === 'file') {
                this.addTestResult(testName, true, `Размер: ${result.size} байт`);
            } else {
                this.addTestResult(testName, false, result.error || 'Неверная информация');
            }
        } catch (error) {
            this.addTestResult(testName, false, error.message);
        }
    }

    /**
     * Тест дерева директорий
     */
    async testDirectoryTree() {
        const testName = 'Дерево директорий';
        try {
            const result = await this.tool.execute({
                action: 'tree',
                data: {
                    path: this.testDir,
                    depth: 2
                }
            });

            if (result.success && result.tree) {
                this.addTestResult(testName, true, 'Дерево построено успешно');
            } else {
                this.addTestResult(testName, false, result.error || 'Дерево не построено');
            }
        } catch (error) {
            this.addTestResult(testName, false, error.message);
        }
    }

    /**
     * Тест создания директории
     */
    async testCreateDirectory() {
        const testName = 'Создание директории';
        try {
            const result = await this.tool.execute({
                action: 'create',
                data: {
                    path: path.join(this.testDir, 'new_subdir'),
                    recursive: true
                }
            });

            if (result.success) {
                this.addTestResult(testName, true, 'Директория создана');
            } else {
                this.addTestResult(testName, false, result.error);
            }
        } catch (error) {
            this.addTestResult(testName, false, error.message);
        }
    }

    /**
     * Тест удаления файла
     */
    async testDeleteFile() {
        const testName = 'Удаление файла';
        try {
            const result = await this.tool.execute({
                action: 'delete',
                data: {
                    path: path.join(this.testDir, 'test_moved.txt')
                }
            });

            if (result.success) {
                this.addTestResult(testName, true, 'Файл удалён');
            } else {
                this.addTestResult(testName, false, result.error);
            }
        } catch (error) {
            this.addTestResult(testName, false, error.message);
        }
    }

    /**
     * Тест статуса файловой системы
     */
    async testFileSystemStatus() {
        const testName = 'Статус файловой системы';
        try {
            const result = await this.tool.execute({
                action: 'status',
                data: {}
            });

            if (result.success && result.currentDirectory) {
                this.addTestResult(testName, true, `Платформа: ${result.platform}`);
            } else {
                this.addTestResult(testName, false, result.error || 'Статус не получен');
            }
        } catch (error) {
            this.addTestResult(testName, false, error.message);
        }
    }

    /**
     * Добавление результата теста
     */
    addTestResult(testName, success, message) {
        this.testResults.push({
            name: testName,
            success: success,
            message: message
        });

        const icon = success ? '✅' : '❌';
        console.log(`${icon} ${testName}: ${message}`);
    }

    /**
     * Вывод итоговых результатов
     */
    printResults() {
        const totalTests = this.testResults.length;
        const passedTests = this.testResults.filter(r => r.success).length;
        const failedTests = totalTests - passedTests;

        console.log('\n📊 Итоговые результаты тестирования:');
        console.log(`   Всего тестов: ${totalTests}`);
        console.log(`   Пройдено: ${passedTests} ✅`);
        console.log(`   Провалено: ${failedTests} ❌`);
        console.log(`   Успешность: ${Math.round((passedTests / totalTests) * 100)}%`);

        if (failedTests > 0) {
            console.log('\n❌ Провалившиеся тесты:');
            this.testResults
                .filter(r => !r.success)
                .forEach(r => console.log(`   - ${r.name}: ${r.message}`));
        }

        console.log('\n🎉 Тестирование завершено!');
    }
}

// Запуск тестов если файл выполняется напрямую
if (require.main === module) {
    const tester = new FileSystemToolTester();
    tester.runAllTests().catch(console.error);
}

module.exports = { FileSystemToolTester };