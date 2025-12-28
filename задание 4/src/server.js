const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');
const db = require('./db');

const PROTO_PATH = path.join(__dirname, '..', 'proto', 'glossary.proto');

// Загрузка proto-файла
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const glossaryProto = grpc.loadPackageDefinition(packageDefinition).glossary;

/**
 * Получить все термины
 */
function getTerms(call, callback) {
  console.log('[GetTerms] Запрос списка всех терминов');
  try {
    const terms = db.getAllTerms();
    console.log(`[GetTerms] Найдено ${terms.length} терминов`);
    callback(null, { terms });
  } catch (error) {
    console.error('[GetTerms] Ошибка:', error.message);
    callback({
      code: grpc.status.INTERNAL,
      message: error.message,
    });
  }
}

/**
 * Получить термин по ключевому слову
 */
function getTerm(call, callback) {
  try {
    const { term } = call.request;
    console.log(`[GetTerm] Запрос термина "${term}"`);

    if (!term) {
      console.warn('[GetTerm] Термин не указан');
      return callback({
        code: grpc.status.INVALID_ARGUMENT,
        message: 'Термин не указан',
      });
    }

    const result = db.getTermByName(term);

    if (!result) {
      console.warn(`[GetTerm] Термин "${term}" не найден`);
      return callback({
        code: grpc.status.NOT_FOUND,
        message: `Термин '${term}' не найден`,
      });
    }

    console.log(`[GetTerm] Термин "${term}" найден (ID: ${result.id})`);
    callback(null, result);
  } catch (error) {
    console.error('[GetTerm] Ошибка:', error.message);
    callback({
      code: grpc.status.INTERNAL,
      message: error.message,
    });
  }
}

/**
 * Создать новый термин
 */
function createTerm(call, callback) {
  try {
    const { term, definition } = call.request;
    console.log(`[CreateTerm] Попытка создать термин "${term}"`);

    if (!term || !definition) {
      console.warn('[CreateTerm] Термин или описание не указаны');
      return callback({
        code: grpc.status.INVALID_ARGUMENT,
        message: 'Термин и описание обязательны',
      });
    }

    const result = db.createTerm(term, definition);

    if (!result) {
      console.warn(`[CreateTerm] Термин "${term}" уже существует`);
      return callback({
        code: grpc.status.ALREADY_EXISTS,
        message: `Термин '${term}' уже существует`,
      });
    }

    console.log(`[CreateTerm] Термин "${term}" создан (ID: ${result.id})`);
    callback(null, result);
  } catch (error) {
    console.error('[CreateTerm] Ошибка:', error.message);
    callback({
      code: grpc.status.INTERNAL,
      message: error.message,
    });
  }
}

/**
 * Обновить термин
 */
function updateTerm(call, callback) {
  try {
    const { term, definition } = call.request;
    console.log(`[UpdateTerm] Попытка обновить термин "${term}"`);

    if (!term || !definition) {
      console.warn('[UpdateTerm] Термин или описание не указаны');
      return callback({
        code: grpc.status.INVALID_ARGUMENT,
        message: 'Термин и описание обязательны',
      });
    }

    const result = db.updateTerm(term, definition);

    if (!result) {
      console.warn(`[UpdateTerm] Термин "${term}" не найден`);
      return callback({
        code: grpc.status.NOT_FOUND,
        message: `Термин '${term}' не найден`,
      });
    }

    console.log(`[UpdateTerm] Термин "${term}" обновлен`);
    callback(null, result);
  } catch (error) {
    console.error('[UpdateTerm] Ошибка:', error.message);
    callback({
      code: grpc.status.INTERNAL,
      message: error.message,
    });
  }
}

/**
 * Удалить термин
 */
function deleteTerm(call, callback) {
  try {
    const { term } = call.request;
    console.log(`[DeleteTerm] Попытка удалить термин "${term}"`);

    if (!term) {
      console.warn('[DeleteTerm] Термин не указан');
      return callback({
        code: grpc.status.INVALID_ARGUMENT,
        message: 'Термин не указан',
      });
    }

    const success = db.deleteTerm(term);

    if (!success) {
      console.warn(`[DeleteTerm] Термин "${term}" не найден`);
      return callback({
        code: grpc.status.NOT_FOUND,
        message: `Термин '${term}' не найден`,
      });
    }

    console.log(`[DeleteTerm] Термин "${term}" удален`);
    callback(null, {
      success: true,
      message: `Термин '${term}' успешно удален`,
    });
  } catch (error) {
    console.error('[DeleteTerm] Ошибка:', error.message);
    callback({
      code: grpc.status.INTERNAL,
      message: error.message,
    });
  }
}

/**
 * Запуск сервера
 */
function main() {
  const server = new grpc.Server();

  server.addService(glossaryProto.GlossaryService.service, {
    getTerms,
    getTerm,
    createTerm,
    updateTerm,
    deleteTerm,
  });

  const PORT = process.env.PORT || '50051';
  const HOST = process.env.HOST || '0.0.0.0';

  server.bindAsync(`${HOST}:${PORT}`, grpc.ServerCredentials.createInsecure(), (error, port) => {
    if (error) {
      console.error('[Server] Ошибка запуска:', error);
      process.exit(1);
    }
    console.log('='.repeat(60));
    console.log('gRPC Glossary Server запущен');
    console.log(`Адрес: ${HOST}:${port}`);
    console.log('Доступные методы: GetTerms, GetTerm, CreateTerm, UpdateTerm, DeleteTerm');
    console.log('='.repeat(60));
    console.log('');
  });
}

main();
