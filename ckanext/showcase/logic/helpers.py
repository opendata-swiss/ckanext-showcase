import ckan.lib.helpers as h
from ckan.plugins import toolkit as tk


def facet_remove_field(key, value=None, replace=None):
    '''
    A custom remove field function to be used by the Showcase search page to
    render the remove link for the tag pills.
    '''
    return h.remove_url_param(
        key, value=value, replace=replace,
        controller='ckanext.showcase.controller:ShowcaseController',
        action='search')


def get_site_statistics():
    '''
    Custom stats helper, so we can get the correct number of packages, and a
    count of showcases.
    '''

    stats = {}
    stats['showcase_count'] = tk.get_action('package_search')(
        {}, {"rows": 1, 'fq': '+dataset_type:showcase'})['count']
    stats['dataset_count'] = tk.get_action('package_search')(
        {}, {"rows": 1, 'fq': '!dataset_type:showcase'})['count']
    stats['group_count'] = len(tk.get_action('group_list')({}, {}))
    stats['organization_count'] = len(
        tk.get_action('organization_list')({}, {}))

    return stats


def create_showcase_types():
    """
    Create tags and vocabulary for showcase types, if they don't exist already.
    """
    user = tk.get_action("get_site_user")({"ignore_auth": True}, ())
    context = {"user": user["name"]}
    try:
        # TODO: this is a workaround copied from https://github.com/ckan/ckanext-dcat/commit/bd490115da8087a14b9a2ef603328e69535144bb
        # When we upgrade CKAN, we should be able to remove this.
        from paste.registry import Registry
        from ckan.lib.cli import MockTranslator
        registry = Registry()
        registry.prepare()
        from pylons import translator
        registry.register(translator, MockTranslator())

        data = {"id": "showcase_types"}
        tk.get_action("vocabulary_show")(context, data)
    except tk.ObjectNotFound:
        data = {"name": "showcase_types"}
        vocab = tk.get_action("vocabulary_create")(context, data)
        for tag in (
                "Application",
                "Data visualisation",
                "Event",
                "Blog and media articles",
                "Paper"
        ):
            data = {"name": tag, "vocabulary_id": vocab["id"]}
            tk.get_action("tag_create")(context, data)


def showcase_types():
    """
    Return the list of showcase types from the showcase_types vocabulary.
    """
    create_showcase_types()
    try:
        showcase_types = tk.get_action("tag_list")(
            data_dict={"vocabulary_id": "showcase_types"}
        )
        return showcase_types
    except tk.ObjectNotFound:
        return None