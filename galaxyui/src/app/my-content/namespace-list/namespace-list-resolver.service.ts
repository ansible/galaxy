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
import { AuthService }           from "../../auth/auth.service";

@Injectable()
export class NamespaceListResolver implements Resolve<Namespace[]> {

    constructor(
    	private namespaceService: NamespaceService,
    	private router: Router,
    	private authService: AuthService) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Namespace[]> {
        return this.namespaceService.query({'page_size': 1000, 'owners__username': this.authService.meCache.username});
    }
}
