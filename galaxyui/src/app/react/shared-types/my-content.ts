import { CollectionList } from '../../resources/collections/collection';

// Adds an optional loading property so we can display when a collection is
// being loaded.
export class ModifiedCollectionList extends CollectionList {
    loading?: boolean;
}
