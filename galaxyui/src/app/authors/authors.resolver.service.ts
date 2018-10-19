import { Injectable } from '@angular/core';

import {
    ActivatedRouteSnapshot,
    Resolve,
    RouterStateSnapshot,
} from '@angular/router';

import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { Namespace } from '../resources/namespaces/namespace';
import { NamespaceService } from '../resources/namespaces/namespace.service';
import { PagedResponse } from '../resources/paged-response';
import { RepositoryService } from '../resources/repositories/repository.service';

@Injectable()
export class NamespaceListResolver implements Resolve<PagedResponse> {
    constructor(private namespaceService: NamespaceService) {}
    resolve(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot,
    ): Observable<PagedResponse> {
        return this.namespaceService.pagedQuery({ is_vendor: false });
    }
}

@Injectable()
export class NamespaceDetailResolver implements Resolve<Namespace> {
    constructor(private namespaceService: NamespaceService) {}
    resolve(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot,
    ): Observable<Namespace> {
        const namespace = route.params['namespace'].toLowerCase();
        const params = {
            name__iexact: namespace,
        };
        return this.namespaceService.query(params).pipe(
            map(results => {
                if (results && results.length) {
                    return results[0] as Namespace;
                } else {
                    return {} as Namespace;
                }
            }),
        );
    }
}

@Injectable()
export class RepositoryResolver implements Resolve<PagedResponse> {
    constructor(private repositoryService: RepositoryService) {}
    resolve(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot,
    ): Observable<PagedResponse> {
        const namespace = route.params['namespace'].toLowerCase();
        const params = {
            provider_namespace__namespace__name__iexact: namespace,
        };
        return this.repositoryService.pagedQuery(params);
    }
}
