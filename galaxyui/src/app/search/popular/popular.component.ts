import {
    Component,
    EventEmitter,
    Input,
    ViewChild,
    OnInit,
    Output
} from '@angular/core';

import {
    ActivatedRoute,
} from '@angular/router';

import { ListConfig }     from 'patternfly-ng/list/basic-list/list-config';
import { ListEvent }      from 'patternfly-ng/list/list-event';

import { Tag }              from '../../resources/tags/tag';
import { TagsService }      from '../../resources/tags/tags.service';

import { PlatformService }  from '../../resources/platforms/platform.service';
import { Platform }         from '../../resources/platforms/platform';

import { CloudPlatformService } from '../../resources/cloud-platforms/cloud-platform.service';
import { CloudPlatform }        from '../../resources/cloud-platforms/cloud-platform';

class PopularData {
    tags: Tag[];
    cloudPlatforms: CloudPlatform[];
    platforms: Platform[];
}

export class PopularEvent {
    itemType: string;
    item: any;
}

@Component({
    selector: 'popular-widget',
    templateUrl: './popular.component.html',
    styleUrls: ['./popular.component.less']
})
export class PopularComponent implements OnInit {

    @Input() popularType: string;
    @Input() popularTitle: string;
    @Output() click = new EventEmitter<PopularEvent>();

    data: PopularData;
    listConfig: ListConfig;
    items: any;

    constructor(
        private tagsService: TagsService,
        private platformService: PlatformService,
        private cloudPlatformService: CloudPlatformService,
        private route: ActivatedRoute
    ) {}

    handleClick($event) {
        // User clicked on an item
        const e = new PopularEvent();
        e.itemType = this.popularType;
        e.item = $event.item;
        this.click.emit(e);
    }

    ngOnInit() {
        this.route.data.subscribe(result => {
            switch (this.popularType) {
                case 'platforms':
                    this.items = result.popularPlatforms.slice(0, 11);
                    break;
                case 'tags':
                    this.items = result.popularTags.slice(0, 11);
                    break;
                case 'cloudPlatforms':
                    this.items = result.popularCloudPlatforms.slice(0, 11);
                    break;
            }
        });
    }
}
