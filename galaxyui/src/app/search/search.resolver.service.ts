import { Injectable } from '@angular/core';

import { ActivatedRouteSnapshot, Resolve, RouterStateSnapshot } from '@angular/router';

import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { ContentResponse } from '../resources/content-search/content';
import { ContentSearchService } from '../resources/content-search/content-search.service';

import { Platform } from '../resources/platforms/platform';
import { PlatformService } from '../resources/platforms/platform.service';

import { ContentType } from '../resources/content-types/content-type';
import { ContentTypeService } from '../resources/content-types/content-type.service';

import { CloudPlatform } from '../resources/cloud-platforms/cloud-platform';
import { CloudPlatformService } from '../resources/cloud-platforms/cloud-platform.service';

import { Tag } from '../resources/tags/tag';
import { TagsService } from '../resources/tags/tags.service';

import { ContributorTypes } from '../enums/contributor-types.enum';

// This class represents the default set of filters to be used when the search
// page is loaded without any params specified
export class DefaultParams {
    static params = {
        // vendor: 'false',
        // deprecated: 'false',
        order_by: '-relevance',
    };

    static getParamString(): string {
        let paramString = '';
        for (const key of Object.keys(this.params)) {
            paramString += key + '=' + encodeURIComponent(this.params[key]) + '&';
        }

        // Remove trailing '&'
        return paramString.substring(0, paramString.length - 1);
    }
}

@Injectable()
export class SearchContentResolver implements Resolve<ContentResponse> {
    constructor(private contentService: ContentSearchService) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<ContentResponse> {
        let params = '';
        for (const key in route.queryParams) {
            if (route.queryParams.hasOwnProperty(key)) {
                if (params !== '') {
                    params += '&';
                }
                if (key === 'contributor_type') {
                    switch (route.queryParams[key]) {
                        case ContributorTypes.community:
                            params += 'vendor=false';
                            break;
                        case ContributorTypes.vendor:
                            params += 'vendor=true';
                    }
                } else {
                    params += `${key}=${encodeURIComponent(route.queryParams[key])}`;
                }
            }
        }
        if (params === '') {
            params += DefaultParams.getParamString();
        }
        // if order_by has not been specified yet, make sure it gets set
        if (!route.queryParams['order_by']) {
            if (params !== '') {
                params += '&';
            }
            params += 'order_by=-relevance';
        }
        return this.contentService.query(params);
    }
}

@Injectable()
export class SearchPlatformResolver implements Resolve<Platform[]> {
    constructor(private platformService: PlatformService) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Platform[]> {
        return this.platformService.query({ page_size: 1000 });
    }
}

@Injectable()
export class SearchContentTypeResolver implements Resolve<ContentType[]> {
    constructor(private contentTypeService: ContentTypeService) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<ContentType[]> {
        return this.contentTypeService.query({ page_size: 1000, order: 'description' });
    }
}

@Injectable()
export class SearchCloudPlatformResolver implements Resolve<CloudPlatform[]> {
    constructor(private contentTypeService: CloudPlatformService) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<CloudPlatform[]> {
        return this.contentTypeService.query({ page_size: 1000 });
    }
}

@Injectable()
export class PopularTagsResolver implements Resolve<Tag[]> {
    constructor(private tagsService: TagsService) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Tag[]> {
        return this.tagsService.search({ order_by: '-roles_count,name' });
    }
}

@Injectable()
export class PopularPlatformsResolver implements Resolve<Platform[]> {
    constructor(private platformService: PlatformService) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Platform[]> {
        return this.platformService.search({ page_size: 1000, order_by: '-roles_count,name' }).pipe(
            map(result => {
                // Sum roles_count per platforms, sans release
                const summary = {};
                const platforms: Platform[] = [];
                result.forEach((item: Platform) => {
                    if (summary[item.name] === undefined) {
                        summary[item.name] = 0;
                    }
                    summary[item.name] += item.roles_count;
                });
                for (const key in summary) {
                    if (summary.hasOwnProperty(key)) {
                        platforms.push({
                            name: key,
                            roles_count: summary[key],
                        } as Platform);
                    }
                }
                return platforms;
            }),
        );
    }
}

@Injectable()
export class PopularCloudPlatformsResolver implements Resolve<CloudPlatform[]> {
    constructor(private cloudPlatformService: CloudPlatformService) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<CloudPlatform[]> {
        return this.cloudPlatformService.search({ order_by: '-roles_count,name' });
    }
}
