import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';

import { ActivatedRoute } from '@angular/router';

import { ListConfig } from 'patternfly-ng/list/basic-list/list-config';

import { Tag } from '../../resources/tags/tag';

import { Platform } from '../../resources/platforms/platform';

import { CloudPlatform } from '../../resources/cloud-platforms/cloud-platform';

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
    styleUrls: ['./popular.component.less'],
})
export class PopularComponent implements OnInit {
    @Input()
    popularType: string;
    @Input()
    popularTitle: string;
    @Output()
    emitItem = new EventEmitter<PopularEvent>();

    data: PopularData;
    listConfig: ListConfig;
    items: any;

    constructor(private route: ActivatedRoute) {}

    handleClick(item) {
        // User clicked on an item
        const e = new PopularEvent();
        e.itemType = this.popularType;
        e.item = item;
        this.emitItem.emit(e);
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
                case 'cloud_platforms':
                    this.items = result.popularCloudPlatforms.slice(0, 11);
                    break;
            }
        });
    }
}
