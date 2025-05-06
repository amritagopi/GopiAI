/**
 * Скрипт для установки MCP серверов
 */
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Путь к файлу конфигурации
const configPath = path.join(__dirname, '..', 'mcp.json');

// Чтение конфигурации
console.log('Чтение конфигурации MCP...');
let config;
try {
    const configData = fs.readFileSync(configPath, 'utf8');
    config = JSON.parse(configData);
} catch (error) {
    console.error(`Ошибка при чтении конфигурации: ${error.message}`);
    process.exit(1);
}

// Получение списка пакетов для установки
if (!config.servers || !Array.isArray(config.servers)) {
    console.error('Ошибка: в конфигурации не найдены сервера или секция "servers" не является массивом');
    process.exit(1);
}

const packages = config.servers
    .filter(server => server.package)
    .map(server => server.package);

if (packages.length === 0) {
    console.log('Не найдены пакеты для установки');
    process.exit(0);
}

// Установка пакетов
console.log(`Установка ${packages.length} пакетов:`);
packages.forEach(pkg => console.log(` - ${pkg}`));

try {
    // Сначала очистим кеш NPM для пакетов
    console.log('\nОчистка кеша NPM...');
    execSync('npm cache clean --force', { stdio: 'inherit' });

    // Затем установим пакеты глобально
    console.log('\nУстановка пакетов...');
    execSync(`npm install -g ${packages.join(' ')}`, { stdio: 'inherit' });

    console.log('\nУстановка успешно завершена!');
} catch (error) {
    console.error(`\nОшибка при установке пакетов: ${error.message}`);

    // Дополнительная информация для отладки
    console.log('\nПроверка доступности пакетов в реестре NPM:');
    packages.forEach(pkg => {
        try {
            execSync(`npm view ${pkg} name`, { stdio: 'pipe' });
            console.log(` - ${pkg}: доступен`);
        } catch (e) {
            console.log(` - ${pkg}: недоступен`);
        }
    });

    console.log('\nВозможные решения:');
    console.log(' 1. Проверьте подключение к интернету');
    console.log(' 2. Проверьте правильность имен пакетов в mcp.json');
    console.log(' 3. Попробуйте установить пакеты вручную:');
    packages.forEach(pkg => {
        console.log(`    npm install -g ${pkg}`);
    });

    process.exit(1);
}

// Проверка создания директории для базы данных
if (config.database && config.database.path) {
    const dbPath = path.join(__dirname, '..', config.database.path);
    const dbDir = path.dirname(dbPath);

    console.log('\nПроверка директории для базы данных...');
    if (!fs.existsSync(dbDir)) {
        console.log(`Создание директории: ${dbDir}`);
        try {
            fs.mkdirSync(dbDir, { recursive: true });
            console.log('Директория успешно создана');
        } catch (error) {
            console.error(`Ошибка при создании директории: ${error.message}`);
        }
    } else {
        console.log('Директория для базы данных уже существует');
    }
}
