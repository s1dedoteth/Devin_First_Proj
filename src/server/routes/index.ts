import type { ServerRoute } from '@hapi/hapi';
import { decodeRoute } from './decode';
import { decodeIdRoute } from './decodeId';
import { searchIdRoute } from './searchId';
import { searchPnRoute } from './searchPn';
import { summaryRoute } from './summary';
import { summaryIdRoute } from './summaryId';
import { infoRoute } from './info';

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
