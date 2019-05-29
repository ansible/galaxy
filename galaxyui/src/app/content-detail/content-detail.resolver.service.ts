import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

import { ActivatedRouteSnapshot, Resolve } from '@angular/router';

import { RepoOrCollectionService } from '../resources/combined/combined.service';
import { RepoOrCollectionResponse } from '../resources/combined/combined';
import { catchError } from 'rxjs/operators';
import { of } from 'rxjs';

@Injectable()
export class TypeCheckResolver implements Resolve<RepoOrCollectionResponse> {
    constructor(
        private repoOrCollectionService: RepoOrCollectionService,
        private router: Router,
    ) {}

    resolve(route: ActivatedRouteSnapshot) {
        const namespace = route.params['namespace'];
        const collection = route.params['name'];

        return this.repoOrCollectionService.query(namespace, collection).pipe(
            catchError(err => {
                this.router.navigate(['not-found']);

                return of(err as RepoOrCollectionResponse);
            }),
        );
    }
}
