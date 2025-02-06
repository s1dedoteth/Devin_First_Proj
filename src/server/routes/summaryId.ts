import { type ServerRoute, type Request, type ResponseToolkit } from '@hapi/hapi';
import { DatabaseManager } from '../../database/DatabaseManager.js';
import Joi from 'joi';

export const summaryIdRoute: ServerRoute = {
  method: 'GET',
  path: '/summaryId',
  options: {
    validate: {
      query: Joi.object({
        id: Joi.string().required(),
        lang: Joi.string().allow(null).default(null)
      })
    }
  },
  handler: async (request: Request, h: ResponseToolkit) => {
    try {
      const { id, lang } = request.query as { id: string; lang: string | null };
      const dbManager = DatabaseManager.getInstance();
      const info = dbManager.getIdSummary(id, lang);
      return h.response(info).type('application/json');
    } catch (error) {
      return h.response({
        error: error instanceof Error ? error.message : 'Unknown error'
      }).code(500);
    }
  }
};
