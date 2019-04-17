import { Injectable } from '@angular/core';

import { ActivatedRouteSnapshot, Resolve } from '@angular/router';

import { Observable } from 'rxjs';
import { AuthService } from '../../auth/auth.service';
import { ImportsService } from '../../resources/imports/imports.service';
import { NamespaceService } from '../../resources/namespaces/namespace.service';
import { PagedResponse } from '../../resources/paged-response';

@Injectable()
export class UserNamespacesResolver implements Resolve<PagedResponse> {
    constructor(
        private namespaceService: NamespaceService,
        private authService: AuthService,
    ) {}

    resolve(route: ActivatedRouteSnapshot): Observable<PagedResponse> {
        return this.namespaceService.pagedQuery({
            owners__username: this.authService.meCache.username,
            page_size: 100,
        });
    }
}

@Injectable()
export class ImportListResolver implements Resolve<PagedResponse> {
    constructor(private importsService: ImportsService) {}

    resolve(route: ActivatedRouteSnapshot): Observable<PagedResponse> {
        return this.importsService.get_import_list(
            route.params['namespaceid'],
            route.queryParams,
        );
    }
}
