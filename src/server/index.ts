import * as Hapi from '@hapi/hapi';
import { routes } from './routes/index.js';
import { DatabaseManager } from '../database/DatabaseManager.js';
import { ProcessorManager } from '../processors/ProcessorManager.js';
import { DefaultProcessor } from '../processors/DefaultProcessor.js';
import { FlashDetector } from '../core/FlashDetector.js';

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
