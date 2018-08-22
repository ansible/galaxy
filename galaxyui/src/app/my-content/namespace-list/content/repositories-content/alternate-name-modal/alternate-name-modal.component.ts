import { Component, OnInit } from '@angular/core';

import { AbstractControl, FormControl, ValidatorFn, Validators } from '@angular/forms';

import { BsModalRef } from 'ngx-bootstrap';

import { Repository } from '../../../../../resources/repositories/repository';
import { RepositoryService } from '../../../../../resources/repositories/repository.service';
import { RepositoryImportService } from '../../../../../resources/repository-imports/repository-import.service';

export function forbiddenCharValidator(): ValidatorFn {
    const charRE = new RegExp('[^0-9A-Za-z-_]');
    return (control: AbstractControl): { [key: string]: any } => {
        const forbidden = charRE.test(control.value);
        return forbidden ? { forbiddenChar: { value: control.value } } : null;
    };
}

export function forbiddenFirstCharValidator(): ValidatorFn {
    const charRE = new RegExp('^[A-Za-z0-9]');
    return (control: AbstractControl): { [key: string]: any } => {
        const forbidden = !charRE.test(control.value);
        return forbidden ? { forbiddenFirstChar: { value: control.value } } : null;
    };
}

export function forbiddenLastCharValidator(): ValidatorFn {
    const charRE = new RegExp('[A-Za-z0-9]$');
    return (control: AbstractControl): { [key: string]: any } => {
        const forbidden = !charRE.test(control.value);
        return forbidden ? { forbiddenLastChar: { value: control.value } } : null;
    };
}

@Component({
    selector: 'alternate-name-modale',
    templateUrl: './alternate-name-modal.component.html',
    styleUrls: ['./alternate-name-modal.component.less'],
})
export class AlternateNameModalComponent implements OnInit {
    saveInProgress = false;
    repository: Repository;
    startedImport = false;

    name: FormControl = new FormControl('', [
        Validators.required,
        Validators.minLength(3),
        forbiddenCharValidator(),
        forbiddenFirstCharValidator(),
        forbiddenLastCharValidator(),
    ]);

    constructor(
        public bsModalRef: BsModalRef,
        private repositoryService: RepositoryService,
        private repositoryImportService: RepositoryImportService,
    ) {}

    ngOnInit() {
        this.name.setValue(this.repository.name);
    }

    okIsDisabled(): boolean {
        return !this.name.valid;
    }

    updateRepoName(): void {
        this.saveInProgress = true;
        if (this.name.value !== this.repository.name) {
            const repo: Repository = new Repository();
            repo.id = this.repository.id;
            repo.name = this.name.value;
            repo.original_name = this.repository.original_name;
            repo.description = this.repository.description;
            repo.import_branch = this.repository.import_branch;
            repo.is_enabled = this.repository.is_enabled;
            this.repositoryService.save(repo).subscribe(saveResult => {
                this.repositoryImportService.save({ repository_id: this.repository.id }).subscribe(importResult => {
                    console.log(`Started import for ${this.repository.name}`);
                    this.saveInProgress = true;
                    this.startedImport = true;
                    this.bsModalRef.hide();
                });
            });
        }
    }
}
