import Hapi from '@hapi/hapi';
import { routes } from './routes/index';
import { DatabaseManager } from '../database/DatabaseManager';
import { ProcessorManager } from '../processors/ProcessorManager';
import { DefaultProcessor } from '../processors/DefaultProcessor';
import { FlashDetector } from '../core/FlashDetector';

const init = async () => {
  const server = Hapi.server({
    port: process.env.PORT || 3000,
    host: process.env.HOST || 'localhost'
  });

  // Register routes
  server.route(routes);

  // Initialize database and processors
  const dbManager = DatabaseManager.getInstance();
  await dbManager.loadDatabase(process.env.FDB_PATH || './fdb.json');

  const processorManager = ProcessorManager.getInstance();
  processorManager.registerProcessor(new DefaultProcessor());

  // Initialize flash decoders
  FlashDetector.initialize();

  await server.start();
  console.log('Server running on %s', server.info.uri);

  process.on('unhandledRejection', (err) => {
    console.error('Unhandled rejection:', err);
    process.exit(1);
  });
};

init();
