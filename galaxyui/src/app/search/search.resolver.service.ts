import {
    Injectable
} from '@angular/core';

import {
    ActivatedRouteSnapshot,
    Resolve,
    Router,
    RouterStateSnapshot
} from '@angular/router';

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

@Injectable()
export class SearchContentResolver implements Resolve<ContentResponse> {
    constructor(
        private contentService: ContentSearchService,
        private router: Router
    ){}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<ContentResponse> {
        return this.contentService.query();
    }
}

@Injectable()
export class SearchPlatformResolver implements Resolve<Platform[]> {
    constructor(
        private platformService: PlatformService,
        private router: Router
    ){}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Platform[]> {
        return this.platformService.query({'page_size': 1000});
    }
}

@Injectable()
export class SearchContentTypeResolver implements Resolve<ContentType[]> {
    constructor(
        private contentTypeService: ContentTypeService,
        private router: Router
    ){}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<ContentType[]> {
        return this.contentTypeService.query({'page_size': 1000, 'order': 'description'});
    }
}

@Injectable()
export class SearchCloudPlatformResolver implements Resolve<CloudPlatform[]> {
    constructor(
        private contentTypeService: CloudPlatformService,
        private router: Router
    ){}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<CloudPlatform[]> {
        return this.contentTypeService.query({'page_size': 1000});
    }
}

@Injectable()
export class PopularTagsResolver implements Resolve<Tag[]> {
    constructor(
        private tagsService: TagsService,
        private router: Router
    ){}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Tag[]> {
        return this.tagsService.search({'order_by': '-roles_count'});
    }
}

@Injectable()
export class PopularPlatformsResolver implements Resolve<Platform[]> {
    constructor(
        private platformService: PlatformService,
        private router: Router
    ){}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<Platform[]> {
        return this.platformService.search({'page_size': 1000, 'order_by': '-roles_count'}).map(result => {
            // Sum roles_count per platforms, sans release
            let summary = {}
            let platforms: Platform[] = [];
            result.forEach((item: Platform) => {
                if (summary[item.name] == undefined) {
                    summary[item.name] = 0
                }
                summary[item.name] += item.roles_count;
            });
            for (var key in summary) {
                platforms.push({
                    name: key,
                    roles_count: summary[key]
                } as Platform)
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
    ){}
    resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<CloudPlatform[]> {
        return this.cloudPlatformService.search({'order_by': '-roles_count'});
    }
}
