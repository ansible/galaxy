import { Component, Input, OnInit, EventEmitter, Output } from '@angular/core';

import { CardConfig } from 'patternfly-ng/card/basic-card/card-config';
import { RepoFormats } from '../../../enums/repo-types.enum';
import { Content } from '../../../resources/content/content';
import { Repository } from '../../../resources/repositories/repository';
import { CollectionDetail } from '../../../resources/collections/collection';
import { ViewTypes } from '../../../enums/view-types.enum';

import { cloneDeep } from 'lodash';

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
    install_warn: string;
    download_url: string;
}

@Component({
    selector: 'card-info',
    templateUrl: './card-info.component.html',
    styleUrls: ['./card-info.component.less'],
})
export class CardInfoComponent implements OnInit {
    // Used to track which component is being loaded
    componentName = 'CardInfoComponent';
    all_versions = [];

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
                    `mazer install ${repoContent.summary_fields['namespace']['name']}.` +
                    `${repoContent.summary_fields['repository']['name']}`;
            } else {
                cmd =
                    `ansible-galaxy install ${repoContent.summary_fields['namespace']['name']}.` +
                    `${repoContent.name}`;
            }

            this.infoData.install_cmd = cmd;
            this.infoData.tags = repoContent.summary_fields['tags'];
            this.infoData.min_ansible_version = repoContent.min_ansible_version;
        }
    }

    @Input()
    set collection(col: CollectionDetail) {
        const versions = [];

        const collection = cloneDeep(col);
        let download_url;

        this.all_versions = collection.all_versions;

        for (const version of collection.all_versions) {
            if (version.version !== collection.latest_version.version) {
                version.created = moment(version.created).fromNow();
                versions.push(version);
            } else {
                download_url = version.download_url;
            }
        }
        this.infoData = {
            install_cmd: `ansible-galaxy collection install ${collection.namespace.name}.${collection.name}`,
            tags: collection.latest_version.metadata.tags,
            latest_version: collection.latest_version,
            versions: versions,
            readme: collection.latest_version.readme_html,
            install_warn:
                'Installing collections with ansible-galaxy is only supported in ansible 2.9+',
            download_url: download_url,
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
        install_warn: null,
        download_url: null,
    } as InfoData;

    ngOnInit() {
        this.config = {
            title: 'Info',
            titleBorder: true,
            topBorder: true,
        } as CardConfig;
    }

    updateVersion($event) {
        const version = $event.target.value;
        const cmd = this.infoData.install_cmd.split(':')[0];

        const versionObj = this.all_versions.find(
            x =>
                x.version === (version || this.infoData.latest_version.version),
        );

        if (versionObj) {
            this.infoData.download_url = versionObj.download_url;
        }

        if (version === '') {
            this.infoData.install_cmd = cmd;
        } else {
            this.infoData.install_cmd = `${cmd}:${version}`;
        }
    }

    switchToReadme() {
        this.emitView.emit(ViewTypes.readme);
    }
}
