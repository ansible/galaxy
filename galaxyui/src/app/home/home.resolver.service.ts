import { Injectable } from '@angular/core';

import { ActivatedRouteSnapshot, Resolve, RouterStateSnapshot } from '@angular/router';

import { Observable } from 'rxjs';

import { ContentBlock } from '../resources/content-blocks/content-block';
import { ContentBlocksService } from '../resources/content-blocks/content-blocks.service';
import { NamespaceService } from '../resources/namespaces/namespace.service';
import { PagedResponse } from '../resources/paged-response';

@Injectable()
export class VendorListResolver implements Resolve<PagedResponse> {
    constructor(private namespaceService: NamespaceService) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<PagedResponse> {
        return this.namespaceService.pagedQuery({ is_vendor: 'true' });
    }
}

@Injectable()
export class ContentBlockResolver implements Resolve<ContentBlock[]> {
    constructor(private blockService: ContentBlocksService) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<ContentBlock[]> {
        return this.blockService.query();
    }
}
