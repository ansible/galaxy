import { ProviderNamespace } from "../provider-namespaces/provider-namespace";
import { Repository }        from "../repositories/repository";
import { User }              from "../users/user";

export class Namespace {
    id: number;
    name: string;
    description: string;
    avatar_url: string;
    location: string;
    company: string;
    email: string;
    html_url: string;
    active: boolean;
    owners: User[];
    provider_namespaces: ProviderNamespace[];
    repositories: Repository[];
    summary_fields: any;
}
