import type { ServerRoute, Request, ResponseToolkit } from '@hapi/hapi';
import { DatabaseManager } from '../../database/DatabaseManager.js';
import Joi from 'joi';

export const searchIdRoute: ServerRoute = {
  method: 'GET',
  path: '/searchId',
  options: {
    validate: {
      query: Joi.object({
        id: Joi.string().required(),
        partMatch: Joi.boolean().default(false),
        limit: Joi.number().integer().min(0).default(0)
      })
    }
  },
  handler: async (request, h) => {
    try {
      const { id, partMatch, limit } = request.query as { id: string; partMatch: boolean; limit: number };
      const dbManager = DatabaseManager.getInstance();
      const results = dbManager.searchFlashId(id, partMatch, limit);
      return h.response(results).type('application/json');
    } catch (error) {
      return h.response({
        error: error instanceof Error ? error.message : 'Unknown error'
      }).code(500);
    }
  }
};
