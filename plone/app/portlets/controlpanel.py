from plone.locking.interfaces import ILockSettings
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from zope.component import adapts
from zope.formlib import form
from zope.interface import implements
from zope.interface import Interface
from zope import schema
from zope.site.hooks import getSite

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.controlpanel.form import ControlPanelForm

from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import ObjectWidget
from zope.app.form.browser import ListSequenceWidget

class IPortletControlPanelSchema(ILockSettings):

    css_classes = schema.Text(
        title=_(u"CSS classes"),
        description=_(u""),
        required=False,
    )


class PortletControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IPortletControlPanelSchema)

    def __init__(self, context):
        super(PortletControlPanelAdapter, self).__init__(context)

        self.portal = getSite()
        self.properties_tool = getToolByName(self.portal, 'portal_properties')
        self.context = self.properties_tool.site_properties
        self.encoding = self.properties_tool.site_properties.default_charset

    css_classes = ProxyFieldProperty(IPortletControlPanelSchema['css_classes'])

class PortletControlPanel(ControlPanelForm):

    form_fields = form.FormFields(IPortletControlPanelSchema)

    label = _("Portlet settings")
    description = _("Portlet settings.")
    form_name = _("Portlet settings")
