import {
    Injectable
} from '@angular/core';

import {
    ActivatedRouteSnapshot,
    Resolve,
    Router,
    RouterStateSnapshot
} from '@angular/router';

import { Observable }            from "rxjs/Observable";

import { NamespaceService }      from '../resources/namespaces/namespace.service';
import { Namespace }             from '../resources/namespaces/namespace';
import { PagedResponse }         from '../resources/paged-response';

@Injectable()
export class VendorListResolver implements Resolve<PagedResponse> {
    constructor(
        private namespaceService: NamespaceService,
        private router: Router
    ){}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<PagedResponse> {
        return this.namespaceService.pagedQuery({is_vendor: 'true'});
    }
}
