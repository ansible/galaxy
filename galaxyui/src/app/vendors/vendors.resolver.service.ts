import { Injectable } from '@angular/core';

import { ActivatedRouteSnapshot, Resolve, RouterStateSnapshot } from '@angular/router';

import { Observable } from 'rxjs/Observable';

import { NamespaceService } from '../resources/namespaces/namespace.service';
import { PagedResponse } from '../resources/paged-response';

@Injectable()
export class VendorListResolver implements Resolve<PagedResponse> {
    constructor(private namespaceService: NamespaceService) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<PagedResponse> {
        return this.namespaceService.pagedQuery({ is_vendor: 'true' });
    }
}
