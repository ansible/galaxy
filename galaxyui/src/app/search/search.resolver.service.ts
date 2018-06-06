import {
    Injectable
} from '@angular/core';

import {
    ActivatedRouteSnapshot,
    Resolve,
    Router,
    RouterStateSnapshot
} from '@angular/router';

import {
    Location
} from '@angular/common';

import { Observable }            from 'rxjs/Observable';
import { ContentSearchService }  from '../resources/content-search/content-search.service';
import { ContentResponse }       from '../resources/content-search/content';

import { PlatformService }       from '../resources/platforms/platform.service';
import { Platform }              from '../resources/platforms/platform';

import { ContentTypeService }    from '../resources/content-types/content-type.service';
import { ContentType }           from '../resources/content-types/content-type';

import { CloudPlatformService }  from '../resources/cloud-platforms/cloud-platform.service';
import { CloudPlatform }         from '../resources/cloud-platforms/cloud-platform';

import { TagsService }           from '../resources/tags/tags.service';
import { Tag }                   from '../resources/tags/tag';

import { ContributorTypes }      from '../enums/contributor-types.enum';

@Injectable()
export class SearchContentResolver implements Resolve<ContentResponse> {
    constructor(
        private contentService: ContentSearchService,
        private router: Router,
        private location: Location
    ) {}
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
            // When no prior query, default Contributor Type to vendor.
            params += 'vendor=true';
        }
        // Add default params
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
    constructor(
        private platformService: PlatformService,
        private router: Router
    ) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Platform[]> {
        return this.platformService.query({'page_size': 1000});
    }
}

@Injectable()
export class SearchContentTypeResolver implements Resolve<ContentType[]> {
    constructor(
        private contentTypeService: ContentTypeService,
        private router: Router
    ) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<ContentType[]> {
        return this.contentTypeService.query({'page_size': 1000, 'order': 'description'});
    }
}

@Injectable()
export class SearchCloudPlatformResolver implements Resolve<CloudPlatform[]> {
    constructor(
        private contentTypeService: CloudPlatformService,
        private router: Router
    ) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<CloudPlatform[]> {
        return this.contentTypeService.query({'page_size': 1000});
    }
}

@Injectable()
export class PopularTagsResolver implements Resolve<Tag[]> {
    constructor(
        private tagsService: TagsService,
        private router: Router
    ) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Tag[]> {
        return this.tagsService.search({'order_by': '-roles_count'});
    }
}

@Injectable()
export class PopularPlatformsResolver implements Resolve<Platform[]> {
    constructor(
        private platformService: PlatformService,
        private router: Router
    ) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Platform[]> {
        return this.platformService.search({'page_size': 1000, 'order_by': '-roles_count'}).map(result => {
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
                        roles_count: summary[key]
                    } as Platform);
                }
            }
            return platforms;
        });
    }
}

@Injectable()
export class PopularCloudPlatformsResolver implements Resolve<CloudPlatform[]> {
    constructor(
        private cloudPlatformService: CloudPlatformService,
        private router: Router
    ) {}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<CloudPlatform[]> {
        return this.cloudPlatformService.search({'order_by': '-roles_count'});
    }
}
