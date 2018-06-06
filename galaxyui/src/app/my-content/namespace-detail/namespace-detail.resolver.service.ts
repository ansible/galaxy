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

import { Namespace }         from '../../resources/namespaces/namespace';
import { NamespaceService }  from '../../resources/namespaces/namespace.service';

import {
    AuthService,
    Me
} from '../../auth/auth.service';


@Injectable()
export class NamespaceDetailResolver implements Resolve<Namespace> {
    constructor(
        private namespaceService: NamespaceService,
        private router: Router) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Namespace> {
        const id = route.paramMap.get('id');

        if (id === null || id === 'new') {
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

@Injectable()
export class MeResolver implements Resolve<Me> {
    constructor(
        private authService: AuthService,
        private router: Router) {}

    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Me> {
        console.log('HERE');
        return this.authService.me();
    }
}
