import { Injectable } from '@angular/core';

import {
    ActivatedRouteSnapshot,
    Resolve,
    RouterStateSnapshot,
} from '@angular/router';

import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { Content } from '../resources/content/content';
import { ContentService } from '../resources/content/content.service';
import { Namespace } from '../resources/namespaces/namespace';
import { NamespaceService } from '../resources/namespaces/namespace.service';
import { Repository } from '../resources/repositories/repository';
import { RepositoryService } from '../resources/repositories/repository.service';
import { CollectionDetail } from '../resources/collections/collection';
import { CollectionDetailService } from '../resources/collections/collection.service';

@Injectable()
export class ContentResolver implements Resolve<Content[]> {
    constructor(private contentService: ContentService) {}
    resolve(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot,
    ): Observable<Content[]> {
        const repository = route.params['repository'].toLowerCase();
        const namespace = route.params['namespace'].toLowerCase();
        const name = route.params['content_name'];
        const params = {
            repository__name__iexact: repository,
            repository__provider_namespace__namespace__name__iexact: namespace,
        };
        if (name) {
            params['name'] = name.toLowerCase();
        }
        return this.contentService.query(params);
    }
}

@Injectable()
export class RepositoryResolver implements Resolve<Repository> {
    constructor(private repositoryService: RepositoryService) {}
    resolve(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot,
    ): Observable<Repository> {
        const repository = route.params['repository'].toLowerCase();
        const namespace = route.params['namespace'].toLowerCase();
        const params = {
            name__iexact: repository,
            provider_namespace__namespace__name__iexact: namespace,
        };
        return this.repositoryService
            .query(params)
            .pipe(map(results => results[0]));
    }
}

@Injectable()
export class NamespaceResolver implements Resolve<Namespace> {
    constructor(private namespaceService: NamespaceService) {}
    resolve(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot,
    ): Observable<Namespace> {
        const namespace = route.params['namespace'].toLowerCase();
        const params = {
            name__iexact: namespace,
        };
        return this.namespaceService
            .query(params)
            .pipe(map(results => results[0]));
    }
}

@Injectable()
export class CollectionResolver implements Resolve<CollectionDetail> {
    constructor(private collectionDetailService: CollectionDetailService) {}

    resolve(route: ActivatedRouteSnapshot) {
        const namespace = route.params['namespace'].toLowerCase();
        const collection = route.params['collection'].toLowerCase();

        return this.collectionDetailService.get(namespace, collection);
    }
}
