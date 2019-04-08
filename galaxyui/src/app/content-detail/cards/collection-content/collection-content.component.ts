import { Component, Input, OnInit } from '@angular/core';

@Component({
    selector: 'card-collection-content',
    templateUrl: './collection-content.component.html',
    styleUrls: ['./collection-content.component.less'],
})
export class CardCollectionContentComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'CardCollectionContentComponent';

    constructor() {}

    @Input()
    contents: any[];

    displayedContents: any[];
    textFilter: string;
    typeFilter = {
        role: true,
        module: true,
        playbook: true,
        plugin: true,
    };
    availableTypes: string[];
    appliedTypes: Set<string>;

    ngOnInit() {
        this.displayedContents = this.contents;
        this.availableTypes = Object.keys(this.typeFilter);
        this.appliedTypes = new Set(this.availableTypes);
    }

    getContentTypeClass(type) {
        switch (type) {
            case 'role':
                return 'role';
            case 'module':
                return 'module';
            case 'playbook':
                return 'playbook';
            default:
                return 'plugin';
        }
    }

    filterByKeyword(filter) {
        this.textFilter = filter;
        this.filter();
    }

    filterByType(key) {
        this.appliedTypes = new Set([]);

        this.typeFilter[key] = !this.typeFilter[key];

        for (const type of this.availableTypes) {
            if (this.typeFilter[type]) {
                this.appliedTypes.add(type);
            }
        }

        this.filter();
    }

    private filter() {
        const newContent = [];
        for (const content of this.contents) {
            if (
                content.name.match(this.textFilter) &&
                this.appliedTypes.has(
                    this.getContentTypeClass(content.content_type),
                )
            ) {
                newContent.push(content);
            }
        }

        this.displayedContents = newContent;
    }
}
