import { Injectable } from '@angular/core';

import { ActivatedRouteSnapshot, Resolve } from '@angular/router';

import { CollectionDetail } from '../resources/collections/collection';
import { CollectionDetailService } from '../resources/collections/collection.service';

@Injectable()
export class CollectionResolver implements Resolve<CollectionDetail> {
    constructor(private collectionDetailService: CollectionDetailService) {}

    resolve(route: ActivatedRouteSnapshot) {
        const namespace = route.params['namespace'].toLowerCase();
        const collection = route.params['collection'].toLowerCase();

        return this.collectionDetailService.get(namespace, collection);
    }
}
