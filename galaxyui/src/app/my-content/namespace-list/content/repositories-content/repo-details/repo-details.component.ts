import { Component, OnInit, Input } from '@angular/core';

import { ContentService } from '../../../../../resources/content/content.service';
import { Content } from '../../../../../resources/content/content';

@Component({
    selector: 'app-repo-details',
    templateUrl: './repo-details.component.html',
    styleUrls: ['./repo-details.component.less'],
})
export class RepoDetailsComponent implements OnInit {
    constructor(private contentService: ContentService) {}

    @Input()
    repo;

    repoContent: Content;

    ngOnInit() {}
}
