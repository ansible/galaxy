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

import { Content }               from '../resources/content/content';
import { ContentService }        from '../resources/content/content.service';
import { Namespace }             from '../resources/namespaces/namespace';
import { NamespaceService }      from '../resources/namespaces/namespace.service';
import { Repository }            from '../resources/repositories/repository';
import { RepositoryService }     from '../resources/repositories/repository.service';

@Injectable()
export class ContentResolver implements Resolve<Content[]> {
    constructor(
        private contentService: ContentService,
        private router: Router
    ) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Content[]> {
        const repository = route.params['repository'].toLowerCase();
        const namespace = route.params['namespace'].toLowerCase();
        const name = route.params['content_name'];
        const params = {
            'repository__name__iexact': repository,
            'repository__provider_namespace__namespace__name__iexact': namespace
        };
        if (name) {
            params['name'] = name.toLowerCase();
        }
        return this.contentService.query(params);
    }
}

@Injectable()
export class RepositoryResolver implements Resolve<Repository> {
    constructor(
        private repositoryService: RepositoryService,
        private router: Router
    ) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Repository> {
        const repository = route.params['repository'].toLowerCase();
        const namespace = route.params['namespace'].toLowerCase();
        const params = {
            'name__iexact': repository,
            'provider_namespace__namespace__name__iexact': namespace
        };
        return this.repositoryService.query(params).map(results => results[0]);
    }
}

@Injectable()
export class NamespaceResolver implements Resolve<Namespace> {
    constructor(
        private namespaceService: NamespaceService,
        private router: Router
    ) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Namespace> {
        const namespace = route.params['namespace'].toLowerCase();
        const params = {
            'name__iexact': namespace
        };
        return this.namespaceService.query(params).map(results => results[0]);
    }
}
