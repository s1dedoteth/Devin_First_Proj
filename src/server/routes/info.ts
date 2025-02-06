import * as Hapi from '@hapi/hapi';
import { DatabaseManager } from '../../database/DatabaseManager.js';

export const infoRoute: Hapi.ServerRoute = {
  method: 'GET',
  path: '/info',
  handler: async (request, h) => {
    try {
      const dbManager = DatabaseManager.getInstance();
      const info = dbManager.getDatabaseInfo();
      return h.response(info).type('application/json');
    } catch (error) {
      return h.response({
        error: error instanceof Error ? error.message : 'Unknown error'
      }).code(500);
    }
  }
};
