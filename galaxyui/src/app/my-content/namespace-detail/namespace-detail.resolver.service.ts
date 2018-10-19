import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map, take } from 'rxjs/operators';

import {
    ActivatedRouteSnapshot,
    Resolve,
    Router,
    RouterStateSnapshot,
} from '@angular/router';

import { Namespace } from '../../resources/namespaces/namespace';
import { NamespaceService } from '../../resources/namespaces/namespace.service';

import { AuthService, IMe } from '../../auth/auth.service';

@Injectable()
export class NamespaceDetailResolver implements Resolve<Namespace> {
    constructor(
        private namespaceService: NamespaceService,
        private router: Router,
    ) {}

    resolve(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot,
    ): Observable<Namespace> {
        const id = route.paramMap.get('id');

        if (id === null || id === 'new') {
            return null;
        }

        return this.namespaceService.get(Number(id)).pipe(
            take(1),
            map(namespace => {
                if (namespace) {
                    return namespace;
                } else {
                    this.router.navigate(['/my-content/namespaces/new']);
                    return null;
                }
            }),
        );
    }
}

@Injectable()
export class MeResolver implements Resolve<IMe> {
    constructor(private authService: AuthService) {}

    resolve(
        route: ActivatedRouteSnapshot,
        state: RouterStateSnapshot,
    ): Observable<IMe> {
        return this.authService.me();
    }
}
