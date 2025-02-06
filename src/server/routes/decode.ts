import type { ServerRoute } from '@hapi/hapi';
import { FlashDetector } from '../../core/FlashDetector';
import Joi from 'joi';

export const decodeRoute: ServerRoute = {
  method: 'GET',
  path: '/decode',
  options: {
    validate: {
      query: Joi.object({
        pn: Joi.string().required()
      })
    }
  },
  handler: async (request, h) => {
    try {
      const { pn } = request.query as { pn: string };
      const info = FlashDetector.detect(pn);
      return h.response(info).type('application/json');
    } catch (error) {
      return h.response({
        error: error instanceof Error ? error.message : 'Unknown error'
      }).code(500);
    }
  }
};
