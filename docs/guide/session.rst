Session
=======

Firenado provides a session layer supporting redis or files backends.

To setup the application session it is necessary configure the session section
into the firenado.yml file.

Setting up a redis based session:

.. code-block:: yaml

   session:
    type: redis
    enabled: true
    data:
      source: session

Setting up a file based session:

.. code-block:: yaml

   session:
    type: file
    enabled: true
    path: /tmp

Once a session is set and enabled the developer can persist or retrieve session
data in the handler.

.. code-block:: python

   class SessionCounterHandler(firenado.tornadoweb.TornadoHandler):

       def get(self):
           reset = self.get_argument("reset", False, True)
           if reset:
               # Deleting a session variable
               self.session.delete('counter')
               self.redirect(self.get_rooted_path("/session/counter"))
               return None
           counter = 0
           # Checking if a variable is set in the session
           if self.session.has('counter'):
               # Retrieving a value from the session
               counter = self.session.get('counter')
           counter += 1
           # Setting a value in the session
           self.session.set('counter', counter)
           self.render("session.html", session_value=counter)
