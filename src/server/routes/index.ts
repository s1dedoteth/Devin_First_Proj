import { ServerRoute } from '@hapi/hapi';
import { decodeRoute } from './decode.js';
import { decodeIdRoute } from './decodeId.js';
import { searchIdRoute } from './searchId.js';
import { searchPnRoute } from './searchPn.js';
import { summaryRoute } from './summary.js';
import { summaryIdRoute } from './summaryId.js';
import { infoRoute } from './info.js';

export {
  decodeRoute,
  decodeIdRoute,
  searchIdRoute,
  searchPnRoute,
  summaryRoute,
  summaryIdRoute,
  infoRoute
};

export const routes: ServerRoute[] = [
  decodeRoute,
  decodeIdRoute,
  searchIdRoute,
  searchPnRoute,
  summaryRoute,
  summaryIdRoute,
  infoRoute
];
