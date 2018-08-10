import {
    Injectable
} from '@angular/core';

import {
    ActivatedRouteSnapshot,
    Resolve,
    Router,
    RouterStateSnapshot
} from '@angular/router';

import { Observable }            from 'rxjs/Observable';
import { forkJoin }              from 'rxjs/observable/forkJoin';

import { ContentService }        from '../resources/content/content.service';
import { Content }               from '../resources/content/content';
import { NamespaceService }      from '../resources/namespaces/namespace.service';
import { Namespace }             from '../resources/namespaces/namespace';
import { RepositoryService }     from '../resources/repositories/repository.service';
import { PagedResponse }         from '../resources/paged-response';

@Injectable()
export class NamespaceListResolver implements Resolve<PagedResponse> {
    constructor(
        private namespaceService: NamespaceService,
        private router: Router
    ) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<PagedResponse> {
        return this.namespaceService.pagedQuery({'is_vendor': false});
    }
}

@Injectable()
export class NamespaceDetailResolver implements Resolve<Namespace> {
    constructor(
        private namespaceService: NamespaceService,
        private router: Router
    ) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Namespace> {
        const namespace = route.params['namespace'].toLowerCase();
        const params = {
            name__iexact: namespace
        };
        return this.namespaceService.query(params).map(results => {
            if (results && results.length) {
                return results[0] as Namespace;
            } else {
                return {} as Namespace;
            }
        });
    }
}

@Injectable()
export class RepositoryResolver implements Resolve<PagedResponse> {
    constructor(
        private repositoryService: RepositoryService,
        private router: Router
    ) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<PagedResponse> {
        const namespace = route.params['namespace'].toLowerCase();
        const params = {
            'provider_namespace__namespace__name__iexact': namespace,
        };
        return this.repositoryService.pagedQuery(params);
    }
}
