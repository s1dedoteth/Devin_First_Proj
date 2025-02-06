import type { ServerRoute, Request, ResponseToolkit } from '@hapi/hapi';
import { DatabaseManager } from '../../database/DatabaseManager.js';
import Joi from 'joi';

export const summaryRoute: ServerRoute = {
  method: 'GET',
  path: '/summary',
  options: {
    validate: {
      query: Joi.object({
        pn: Joi.string().required(),
        lang: Joi.string().allow(null).default(null)
      })
    }
  },
  handler: async (request, h) => {
    try {
      const { pn, lang } = request.query as { pn: string; lang: string | null };
      const dbManager = DatabaseManager.getInstance();
      const info = dbManager.getSummary(pn, lang);
      return h.response(info).type('application/json');
    } catch (error) {
      return h.response({
        error: error instanceof Error ? error.message : 'Unknown error'
      }).code(500);
    }
  }
};
