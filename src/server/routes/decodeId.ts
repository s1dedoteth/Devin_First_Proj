import * as Hapi from '@hapi/hapi';
import { FlashDetector } from '../../core/FlashDetector.js';
import Joi from 'joi';

export const decodeIdRoute: Hapi.ServerRoute = {
  method: 'GET',
  path: '/decodeId',
  options: {
    validate: {
      query: Joi.object({
        id: Joi.string().required()
      })
    }
  },
  handler: async (request, h) => {
    try {
      const { id } = request.query as { id: string };
      const info = FlashDetector.decodeFlashId(id);
      return h.response(info).type('application/json');
    } catch (error) {
      return h.response({
        error: error instanceof Error ? error.message : 'Unknown error'
      }).code(500);
    }
  }
};
