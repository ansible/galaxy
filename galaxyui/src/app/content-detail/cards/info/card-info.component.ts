import {
    Component,
    Input,
    OnInit
} from '@angular/core';

import { CardConfig }     from 'patternfly-ng/card/basic-card/card-config';
import { RepoFormats }    from '../../../enums/repo-types.enum';
import { ViewTypes }      from '../../../enums/view-types.enum';
import { Content }        from '../../../resources/content/content';
import { Repository }     from '../../../resources/repositories/repository';

import { ContentTypesPlural }   from '../../../enums/content-types.enum';


@Component({
    selector: 'card-info',
    templateUrl: './card-info.component.html',
    styleUrls: ['./card-info.component.less']
})
export class CardInfoComponent implements OnInit {

    constructor() {}

    _repoContent: Content;
    _metadata: object;
    _repoType: RepoFormats;
    _repository: Repository;

    example_type: string;
    example_type_plural: string;
    example_name: string;

    @Input()
    set repository(data: Repository) {
        this._repository = data;
    }
    get repository(): Repository {
        return this._repository;
    }

    @Input()
    set repoType(repoType: RepoFormats) {
        this._repoType = repoType;
    }
    get repoType(): RepoFormats {
        return this._repoType;
    }

    @Input()
    set metadata(data: object) {
        this._metadata = data;
    }
    get metadata(): object {
        return this._metadata;
    }

    @Input()
    set repoContent(data: Content) {
        this._repoContent = data;
        if (this._repoContent) {
            if (this._repoType === 'multi') {
                this._repoContent['install_cmd'] =
                    `mazer install ${this._repoContent.summary_fields['namespace']['name']}.` +
                    `${this._repoContent.summary_fields['repository']['name']}`;
            } else {
                this._repoContent['install_cmd'] =
                    `ansible-galaxy install ${this._repoContent.summary_fields['namespace']['name']}.` +
                    `${this._repoContent.name}`;
            }
            this._repoContent['tags'] = this._repoContent.summary_fields['tags'];
            this._repoContent['hasTags'] =
                (this.repoContent.summary_fields['tags'] && this._repoContent.summary_fields['tags'].length) ? true : false;
            this.example_name = this._repoContent.name;
            this.example_type = this._repoContent.content_type;
            this.example_type_plural = ContentTypesPlural[this._repoContent.content_type];
        }
    }
    get repoContent(): Content {
        return this._repoContent;
    }


    config: CardConfig;

    ViewTypes: typeof ViewTypes = ViewTypes;
    RepoFormats: typeof RepoFormats = RepoFormats;

    ngOnInit() {
        this.config = {
            title: 'Info',
            titleBorder: true,
            topBorder: true
        } as CardConfig;
    }

    copyToClipboard(elementId: string) {
        const element = document.getElementById(elementId);
        const val = element.textContent;
        const txtArea = document.createElement('textarea');
        txtArea.setAttribute('readonly', '');
        txtArea.style.position = 'absolute';
        txtArea.style.left = '-9999px';
        document.body.appendChild(txtArea);
        txtArea.value = val;
        txtArea.select();
        document.execCommand('copy');
        document.body.removeChild(txtArea);
    }
}
