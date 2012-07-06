import logging
import sys


from zope.component import adapts, getMultiAdapter
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from Acquisition import Explicit, aq_inner, aq_acquire, aq_parent
from Acquisition.interfaces import IAcquirer

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ZODB.POSException import ConflictError

from plone.portlets.interfaces import IPortletRenderer, ILocalPortletAssignable
from plone.portlets.manager import PortletManagerRenderer as BasePortletManagerRenderer
from plone.app.portlets.interfaces import IColumn
from plone.app.portlets.interfaces import IDashboard
#from plone.app.layout.navigation.defaultpage import isDefaultPage
from plone.memoize.view import memoize
from plone.portlets.interfaces import IPortletRetriever
from plone.portlets.utils import hashPortletInfo
from plone.portlets.interfaces import IPortletAssignmentSettings,IPortletAssignmentMapping
from Products.CMFPlone.utils import isDefaultPage


logger = logging.getLogger('portlets')


class PortletManagerRenderer(BasePortletManagerRenderer, Explicit):
    """A Zope 2 implementation of the default PortletManagerRenderer
    """

    @memoize
    def _lazyLoadPortlets(self, manager):
        retriever = getMultiAdapter((self.context, manager), IPortletRetriever)
        items = []
        for p in self.filter(retriever.getPortlets()):
            renderer = self._dataToPortlet(p['assignment'].data)
            info = p.copy()
            info['manager'] = self.manager.__name__
            info['renderer'] = renderer
            hashPortletInfo(info)
            # Record metadata on the renderer
            renderer.__portlet_metadata__ = info.copy()
            del renderer.__portlet_metadata__['renderer']
            try:
                isAvailable = renderer.available
            except ConflictError:
                raise
            except Exception, e:
                isAvailable = False
                logger.exception(
                    "Error while determining renderer availability of portlet "
                    "(%r %r %r): %s" % (
                    p['category'], p['key'], p['name'], str(e)))

            info['available'] = isAvailable

            assignments = info['assignment'].__parent__
            settings = IPortletAssignmentSettings(assignments[info['name']])
            info['settings'] = settings

            items.append(info)

        return items



    def _dataToPortlet(self, data):
        """Helper method to get the correct IPortletRenderer for the given
        data object.
        """
        portlet = getMultiAdapter((self.context, self.request, self.__parent__,
                                        self.manager, data, ), IPortletRenderer)
        return portlet.__of__(self.context)


class ColumnPortletManagerRenderer(PortletManagerRenderer):
    """A renderer for the column portlets
    """
    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IColumn)
    template = ViewPageTemplateFile('browser/templates/column.pt')
    error_message = ViewPageTemplateFile('browser/templates/error_message.pt')

    def _context(self):
        return aq_inner(self.context)

    def base_url(self):
        """If context is a default-page, return URL of folder, else
        return URL of context.
        """
        return str(getMultiAdapter((self._context(), self.request, ), name=u'absolute_url'))

    def can_manage_portlets(self):
        context = self._context()
        ftool = getToolByName(context, 'portal_factory')
        if ftool.isTemporary(context) or \
            not ILocalPortletAssignable.providedBy(context):
            return False
        mtool = getToolByName(context, 'portal_membership')
        return mtool.checkPermission("Portlets: Manage portlets", context)

    def safe_render(self, portlet_renderer):
        try:
            return portlet_renderer.render()
        except ConflictError:
            raise
        except Exception:
            logger.exception('Error while rendering %r' % self)
            aq_acquire(self, 'error_log').raising(sys.exc_info())
            return self.error_message()


    def available(self, info):
        """Only make available on definition context
        """

        if info['settings'].get('is_local_portlet', False):
            compare_context = self.context
            if isDefaultPage(self.context, self.request):
                compare_context = aq_parent(aq_inner(self.context))
            if '/'.join(compare_context.getPhysicalPath()) != info['key']:
                return False

        return True


class DashboardPortletManagerRenderer(ColumnPortletManagerRenderer):
    """Render a column of the dashboard
    """

    adapts(Interface, IDefaultBrowserLayer, IBrowserView, IDashboard)
    template = ViewPageTemplateFile('browser/templates/dashboard-column.pt')
