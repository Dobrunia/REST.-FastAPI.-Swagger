const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

const PROTO_PATH = path.join(__dirname, '..', 'proto', 'glossary.proto');

// Загрузка proto-файла
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true
});

const glossaryProto = grpc.loadPackageDefinition(packageDefinition).glossary;

// Создание клиента
const HOST = process.env.HOST || 'localhost';
const PORT = process.env.PORT || '50051';
const client = new glossaryProto.GlossaryService(
  `${HOST}:${PORT}`,
  grpc.credentials.createInsecure()
);

// Промисификация методов клиента
function promisify(method) {
  return (request) => {
    return new Promise((resolve, reject) => {
      method.call(client, request, (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      });
    });
  };
}

const getTerms = promisify(client.getTerms);
const getTerm = promisify(client.getTerm);
const createTerm = promisify(client.createTerm);
const updateTerm = promisify(client.updateTerm);
const deleteTerm = promisify(client.deleteTerm);

// Вспомогательная функция для вывода
function printTerm(term) {
  console.log(`  ID: ${term.id}`);
  console.log(`  Термин: ${term.term}`);
  console.log(`  Определение: ${term.definition}`);
  console.log(`  Создан: ${term.created_at}`);
  console.log(`  Обновлен: ${term.updated_at}`);
  console.log('');
}

// Демонстрация работы клиента
async function demo() {
  console.log('='.repeat(60));
  console.log('gRPC Glossary Client - Демонстрация');
  console.log('='.repeat(60));
  console.log('');

  try {
    // 1. Создание терминов
    console.log('1. Создание терминов...');
    console.log('-'.repeat(40));
    
    const terms = [
      { term: 'gRPC', definition: 'Google Remote Procedure Call - фреймворк для удаленного вызова процедур' },
      { term: 'Protobuf', definition: 'Protocol Buffers - бинарный формат сериализации данных от Google' },
      { term: 'HTTP/2', definition: 'Вторая версия протокола HTTP с поддержкой мультиплексирования' },
      { term: 'RPC', definition: 'Remote Procedure Call - удаленный вызов процедур' }
    ];

    for (const t of terms) {
      try {
        const created = await createTerm(t);
        console.log(`✓ Создан: ${created.term}`);
      } catch (error) {
        if (error.code === grpc.status.ALREADY_EXISTS) {
          console.log(`⚠ Уже существует: ${t.term}`);
        } else {
          console.log(`✗ Ошибка: ${error.message}`);
        }
      }
    }
    console.log('');

    // 2. Получение всех терминов
    console.log('2. Получение всех терминов...');
    console.log('-'.repeat(40));
    
    const allTerms = await getTerms({});
    console.log(`Найдено терминов: ${allTerms.terms.length}`);
    console.log('');
    
    for (const term of allTerms.terms) {
      printTerm(term);
    }

    // 3. Получение конкретного термина
    console.log('3. Получение термина "gRPC"...');
    console.log('-'.repeat(40));
    
    try {
      const grpcTerm = await getTerm({ term: 'gRPC' });
      printTerm(grpcTerm);
    } catch (error) {
      console.log(`Ошибка: ${error.message}`);
    }

    // 4. Обновление термина
    console.log('4. Обновление термина "gRPC"...');
    console.log('-'.repeat(40));
    
    try {
      const updated = await updateTerm({
        term: 'gRPC',
        definition: 'gRPC - высокопроизводительный RPC-фреймворк от Google, использующий HTTP/2 и Protocol Buffers'
      });
      console.log('✓ Термин обновлен:');
      printTerm(updated);
    } catch (error) {
      console.log(`Ошибка: ${error.message}`);
    }

    // 5. Попытка получить несуществующий термин
    console.log('5. Попытка получить несуществующий термин...');
    console.log('-'.repeat(40));
    
    try {
      await getTerm({ term: 'НесуществующийТермин' });
    } catch (error) {
      console.log(`✓ Ожидаемая ошибка: ${error.details || error.message}`);
    }
    console.log('');

    // 6. Удаление термина
    console.log('6. Удаление термина "RPC"...');
    console.log('-'.repeat(40));
    
    try {
      const result = await deleteTerm({ term: 'RPC' });
      console.log(`✓ ${result.message}`);
    } catch (error) {
      console.log(`Ошибка: ${error.message}`);
    }
    console.log('');

    // 7. Финальный список
    console.log('7. Финальный список терминов...');
    console.log('-'.repeat(40));
    
    const finalTerms = await getTerms({});
    console.log(`Осталось терминов: ${finalTerms.terms.length}`);
    console.log('');
    
    for (const term of finalTerms.terms) {
      console.log(`  • ${term.term}: ${term.definition.substring(0, 50)}...`);
    }

  } catch (error) {
    console.error('Критическая ошибка:', error);
  }

  console.log('');
  console.log('='.repeat(60));
  console.log('Демонстрация завершена');
  console.log('='.repeat(60));
  
  process.exit(0);
}

demo();

