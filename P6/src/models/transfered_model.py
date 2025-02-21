from models.model import Model
from tensorflow.keras import Sequential, layers, models
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.models import load_model

class TransferedModel(Model):
    def _define_model(self, input_shape, categories_count):
        # Load the pre-trained facial expression model
        base_model = load_model('part_six_basic_model.keras')
        
        # Create a new sequential model
        self.model = Sequential([
            # First add the rescaling layer with proper input shape
            layers.Rescaling(1./255, input_shape=input_shape),
            
            # First maxpool to reduce input size
            layers.MaxPooling2D(2),
            
            # Transfer the conv layer
            layers.Conv2D(24, 3, padding='same', activation='relu'),
            
            # Second maxpool
            layers.MaxPooling2D(2)
        ])
        
        # Find the first Conv2D layer in base model
        for i, layer in enumerate(base_model.layers):
            if isinstance(layer, layers.Conv2D):
                # Copy weights from this conv layer to our model's conv layer
                weights = layer.get_weights()[:2]  # Only take the first two weights (kernels and biases)
                self.model.layers[2].set_weights(weights)
                self.model.layers[2].trainable = False
                break
        
        # Add the rest of the layers
        self.model.add(layers.Dropout(0.25))
        self.model.add(layers.Flatten())
        self.model.add(layers.Dense(8, activation='relu'))
        self.model.add(layers.Dropout(0.25))
        self.model.add(layers.Dense(categories_count, activation='softmax'))
    
    def _compile_model(self):
        self.model.compile(
            optimizer=RMSprop(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
