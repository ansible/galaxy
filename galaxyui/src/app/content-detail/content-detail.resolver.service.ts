import { Injectable } from '@angular/core';

import { ActivatedRouteSnapshot, Resolve } from '@angular/router';

import { ContentFormatService } from '../resources/combined/combined.service';
import { ContentFormat } from '../enums/format';

@Injectable()
export class TypeCheckResolver implements Resolve<ContentFormat> {
    constructor(private contentFormatService: ContentFormatService) {}

    resolve(route: ActivatedRouteSnapshot) {
        const namespace = route.params['namespace'].toLowerCase();
        const collection = route.params['name'].toLowerCase();

        return this.contentFormatService.query(namespace, collection);
    }
}
