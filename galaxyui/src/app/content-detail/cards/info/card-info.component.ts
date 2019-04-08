import { Component, Input, OnInit, EventEmitter, Output } from '@angular/core';

import { CardConfig } from 'patternfly-ng/card/basic-card/card-config';
import { RepoFormats } from '../../../enums/repo-types.enum';
import { Content } from '../../../resources/content/content';
import { Repository } from '../../../resources/repositories/repository';
import { CollectionDetail } from '../../../resources/collections/collection';
import { ViewTypes } from '../../../enums/view-types.enum';

import * as moment from 'moment';

class InfoData {
    tags: string[];
    latest_version: any;
    versions: any[];
    last_commit: string;
    last_import: string;
    apb_metadata: string;
    install_cmd: string;
    min_ansible_version: any;
    readme: string;
}

@Component({
    selector: 'card-info',
    templateUrl: './card-info.component.html',
    styleUrls: ['./card-info.component.less'],
})
export class CardInfoComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'CardInfoComponent';

    constructor() {}

    @Output()
    emitView = new EventEmitter<ViewTypes>();

    @Input()
    set repository(repo: Repository) {
        if (repo) {
            this.infoData.last_commit = repo.last_commit;
            this.infoData.last_import = repo.last_import;
        }
    }

    @Input()
    repoType?: RepoFormats;

    @Input()
    set metadata(metadata) {
        this.infoData.apb_metadata = metadata;
    }

    // We're using setter functions here so that the data passed to the
    // component is bound directly to our infoData object, which has to
    // represent collections and repositories
    @Input()
    set repoContent(repoContent: Content) {
        if (repoContent) {
            let cmd;
            if (this.repoType === 'multi') {
                cmd =
                    `mazer install ${
                        repoContent.summary_fields['namespace']['name']
                    }.` + `${repoContent.summary_fields['repository']['name']}`;
            } else {
                cmd =
                    `ansible-galaxy install ${
                        repoContent.summary_fields['namespace']['name']
                    }.` + `${repoContent.name}`;
            }

            this.infoData.install_cmd = cmd;
            this.infoData.tags = repoContent.summary_fields['tags'];
            this.infoData.min_ansible_version = repoContent.min_ansible_version;
        }
    }

    @Input()
    set collection(collection: CollectionDetail) {
        const versions = [];

        for (const version of collection.all_versions) {
            if (version.version !== collection.latest_version.version) {
                version.created = moment(version.created).fromNow();
                versions.push(version);
            }
        }
        this.infoData = {
            install_cmd: `mazer install ${collection.namespace.name}.${
                collection.name
            }`,
            tags: collection.latest_version.metadata.tags,
            latest_version: collection.latest_version,
            versions: versions,
            readme: collection.latest_version.readme_html,
        } as InfoData;
    }

    config: CardConfig;

    infoData = {
        tags: null,
        latest_version: null,
        versions: null,
        last_commit: null,
        last_import: null,
        apb_metadata: null,
        install_cmd: null,
        min_ansible_version: null,
    } as InfoData;

    ngOnInit() {
        this.config = {
            title: 'Info',
            titleBorder: true,
            topBorder: true,
        } as CardConfig;
    }

    updateVersion(version) {
        const cmd = this.infoData.install_cmd.split(',')[0];

        if (version === '') {
            this.infoData.install_cmd = cmd;
        } else {
            this.infoData.install_cmd = `${cmd},version=${version}`;
        }
    }

    switchToReadme() {
        this.emitView.emit(ViewTypes.readme);
    }
}
