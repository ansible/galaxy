import 'rxjs/add/operator/map';
import 'rxjs/add/operator/take';

import { Injectable }        from '@angular/core';
import { Observable }        from 'rxjs/Observable';

import {
    Router,
    Resolve,
    RouterStateSnapshot,
    ActivatedRouteSnapshot
} from '@angular/router';

import { Namespace }         from "../../resources/namespaces/namespace";
import { NamespaceService }  from "../../resources/namespaces/namespace.service";


@Injectable()
export class NamespaceDetailResolver implements Resolve<Namespace> {
    constructor(private namespaceService: NamespaceService, private router: Router) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Namespace> {
        let id = route.paramMap.get('id');

        if (id === 'new') {
            return null;
        }

        return this.namespaceService.get(Number(id)).take(1).map(namespace => {
            if (namespace) {
                return namespace;
            } else {
                this.router.navigate(['/my-content/namespaces/new']);
                return null;
            }
        });
    }
}
