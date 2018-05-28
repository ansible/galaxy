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

import { ContentBlocksService }  from '../resources/content-blocks/content-blocks.service';
import { ContentBlock }          from '../resources/content-blocks/content-block';
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

@Injectable()
export class ContentBlockResolver implements Resolve<ContentBlock[]> {
    constructor(
        private blockService: ContentBlocksService,
        private router: Router
    ){}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<ContentBlock[]> {
        return this.blockService.query();
    }
}
