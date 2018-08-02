import {
    Component,
    EventEmitter,
    Input,
    OnInit,
    Output
} from '@angular/core';

import {
    ActivatedRoute,
} from '@angular/router';

import { ListConfig }     from 'patternfly-ng/list/basic-list/list-config';

import { CloudPlatform }     from '../../resources/cloud-platforms/cloud-platform';
import { EventLoggerService} from '../../resources/logger/event-logger.service';
import { Platform }          from '../../resources/platforms/platform';
import { Tag }               from '../../resources/tags/tag';

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
        private route: ActivatedRoute,
        private eventLoggerService: EventLoggerService,
    ) {}

    handleClick($event) {
        // User clicked on an item
        const e = new PopularEvent();
        e.itemType = this.popularType;
        e.item = $event.item;
        this.click.emit(e);
        this.eventLoggerService.logButton(this.popularTitle + ': ' + $event.item.name);
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
