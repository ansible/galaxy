import { Injectable }                                                   from '@angular/core';

import {
	ActivatedRouteSnapshot,
	Resolve,
	Router,
	RouterStateSnapshot
} from "@angular/router";

import { Observable }            from "rxjs/Observable";
import { NamespaceService }      from "../../resources/namespaces/namespace.service";
import { Namespace }             from "../../resources/namespaces/namespace";
import { PagedResponse }         from '../../resources/paged-response';
import { AuthService }           from "../../auth/auth.service";

@Injectable()
export class NamespaceListResolver implements Resolve<PagedResponse> {

    constructor(
    	private namespaceService: NamespaceService,
    	private router: Router,
    	private authService: AuthService) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<PagedResponse> {
        if (this.authService.meCache.staff) {
            // staff can view and update all namespaces
            return this.namespaceService.pagedQuery({});
        }
        return this.namespaceService.pagedQuery({'owners__username': this.authService.meCache.username});
    }
}
