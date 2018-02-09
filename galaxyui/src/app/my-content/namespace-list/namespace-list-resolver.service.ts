import { Injectable }                                                   from '@angular/core';
import { ActivatedRouteSnapshot, Resolve, Router, RouterStateSnapshot } from "@angular/router";
import { Observable }                                                   from "rxjs/Observable";
import { NamespaceService }                                             from "../../resources/namespaces/namespace.service";
import { Namespace }                                                    from "../../resources/namespaces/namespace";

@Injectable()
export class NamespaceListResolver implements Resolve<Namespace[]> {

    constructor(private namespaceService: NamespaceService, private router: Router) {
    }

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Namespace[]> {
        return this.namespaceService.query();
    }
}
