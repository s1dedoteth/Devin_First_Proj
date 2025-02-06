import type { ServerRoute } from '@hapi/hapi';
import { DatabaseManager } from '../../database/DatabaseManager.js';
import Joi from 'joi';

export const searchPnRoute: ServerRoute = {
  method: 'GET',
  path: '/searchPn',
  options: {
    validate: {
      query: Joi.object({
        pn: Joi.string().required(),
        partMatch: Joi.boolean().default(false),
        limit: Joi.number().integer().min(0).default(0)
      })
    }
  },
  handler: async (request, h) => {
    try {
      const { pn, partMatch, limit } = request.query as { pn: string; partMatch: boolean; limit: number };
      const dbManager = DatabaseManager.getInstance();
      const results = dbManager.searchPartNumber(pn, partMatch, limit);
      return h.response(results).type('application/json');
    } catch (error) {
      return h.response({
        error: error instanceof Error ? error.message : 'Unknown error'
      }).code(500);
    }
  }
};
